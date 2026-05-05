# ─────────────────────────────────────────────────────────────────────────────
# Stage 1 — dependency builder
# Keeps build tools out of the final image.
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.10-slim AS builder

WORKDIR /build

# Install only what's needed to compile wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip wheel --no-cache-dir --wheel-dir /build/wheels -r requirements.txt


# ─────────────────────────────────────────────────────────────────────────────
# Stage 2 — final runtime image
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.10-slim AS runtime

# Security: run as non-root user
RUN groupadd --gid 1001 appgroup \
 && useradd  --uid 1001 --gid appgroup --no-create-home appuser

WORKDIR /app

# Install pre-built wheels from builder stage (no compiler needed)
COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links /wheels /wheels/*.whl \
 && rm -rf /wheels

# Copy application source
COPY --chown=appuser:appgroup . .

# Switch to non-root user
USER appuser

# Expose the application port
EXPOSE 5000

# Health check — Docker will mark the container unhealthy if this fails
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" \
    || exit 1

# ── Production server: gunicorn ───────────────────────────────────────────
# --workers: 2× CPU cores + 1 is the standard heuristic (adjust per host)
# --bind   : listen on all interfaces inside the container
# --timeout: 30 s worker timeout (safe for slow DB queries)
# --access-logfile -: log to stdout (visible via docker logs)
CMD ["gunicorn", \
     "--workers", "2", \
     "--bind", "0.0.0.0:5000", \
     "--timeout", "30", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "app:app"]
