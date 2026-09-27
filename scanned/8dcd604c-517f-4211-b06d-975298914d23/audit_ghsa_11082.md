# [H] OpenClaw has multiple E2E/test Dockerfiles that run all processes as root

## Summary
Severity: High
Advisory: GHSA-w7j5-j98m-w679
CWE: CWE-250
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-w7j5-j98m-w679
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.21

## Details
Three Dockerfiles in scripts/docker/ and scripts/e2e/ lack a USER directive, meaning all processes run as uid 0 (root). If any process is compromised, the attacker has root inside the container, making container breakout significantly easier.
**Partial fix (2026-02-08):** Commit 28e1a65e added USER sandbox to Dockerfile.sandbox and Dockerfile.sandbox-browser. The E2E/test Dockerfiles listed below remain unpatched.

**Affected components:**
- scripts/e2e/Dockerfile
- scripts/e2e/Dockerfile.qr-import
- scripts/docker/install-sh-e2e/Dockerfile
- scripts/docker/install-sh-nonroot/Dockerfile (runs as app but with NOPASSWD sudo — see related advisory)

**Technical Reproduction:**
1. Open each Dockerfile listed above and search for a USER directive — none found.
2. Run any of these containers: docker run --rm -it <image> id
3. Observe: returns uid=0(root).

**Demonstrated Impact:**
- Root inside the container enables kernel exploit attempts, volume mount abuse, and privileged syscall access.
- Test images share the same base (node:22-bookworm) as production, creating risk of accidental deployment of root-running images.

**Environment:** Base images node:22-bookworm and node:22-bookworm-slim default to root. Dockerfile.sandbox and Dockerfile.sandbox-browser were remediated in commit 28e1a65e; only the E2E/test images listed above remain affected.

**Remediation:** Add a USER directive before CMD/ENTRYPOINT in each remaining Dockerfile:
  RUN useradd --create-home --shell /bin/bash appuser
  USER appuser

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-w7j5-j98m-w679
- https://github.com/openclaw/openclaw/commit/28e1a65ebc580f07533966f5693f4df0a18d7085
- https://github.com/openclaw/openclaw
