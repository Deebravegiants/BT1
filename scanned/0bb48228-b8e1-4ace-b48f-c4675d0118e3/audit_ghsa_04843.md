# [H] Crawl4AI: Arbitrary file write (symlink/TOCTOU) plus log and webhook-header injection in Docker server

## Summary
Severity: High
Advisory: GHSA-7cx2-g3h9-382p
CWE: CWE-117, CWE-22, CWE-59, CWE-93
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-7cx2-g3h9-382p
Type: github-advisory

## Affected
- PyPI: `crawl4ai` — affected >=0 <0.8.8

## Details
### Summary

Three backward-compatible hardening fixes in the Docker API server. The headline issue is an arbitrary file write via the screenshot/PDF `output_path`.

### 1. Arbitrary file write via output_path symlink / TOCTOU (primary)

`POST /screenshot` and `POST /pdf` accept an `output_path` constrained to `ALLOWED_OUTPUT_DIR` by `validate_output_path`. The 0.8.7 check was string-only: it did not resolve symlinks, so a symlinked path component inside the output directory could redirect the write outside the directory, and the final `open()` followed symlinks. On a deployment where the runtime user can write executable/cron locations this is an arbitrary-write to code-execution primitive. The API is unauthenticated by default.

Fix: `validate_output_path` now resolves the real path (symlinks) of the parent and re-checks containment, and the write uses `O_NOFOLLOW` (`write_output_file`). `output_path` remains supported.

### 2. CRLF log injection (CWE-117)

User-controlled URLs/errors reflected into log lines could embed CR/LF and forge additional log entries. Fix: a logging filter strips CR/LF/control characters from all records.

### 3. Webhook request-header injection (CWE-93/CWE-113)

User-supplied webhook headers were sent verbatim, allowing CRLF and hop-by-hop / sensitive header injection on the outbound webhook request. Fix: webhook headers are validated (name pattern, no control characters, deny `Host`/`Content-Length`/`Transfer-Encoding`/`Authorization`/`Cookie`/...), with early request-time rejection.

### Impact

Arbitrary file write (potential code execution) for #1; log forging for #2; request smuggling / header injection on outbound webhooks for #3.

### Workarounds

- Upgrade to the patched version.
- Enable authentication (`CRAWL4AI_API_TOKEN`).
- Run the container with a read-only root filesystem.

### Credits

Internal security audit (Crawl4AI maintainers).

## References
- https://github.com/unclecode/crawl4ai/security/advisories/GHSA-7cx2-g3h9-382p
- https://github.com/unclecode/crawl4ai/issues/1
- https://github.com/unclecode/crawl4ai/issues/2
- https://github.com/unclecode/crawl4ai/pull/3
- https://github.com/pypa/advisory-database/tree/main/vulns/crawl4ai/PYSEC-2026-228.yaml
- https://github.com/unclecode/crawl4ai
- https://www.vulncheck.com/advisories/crawl4ai-arbitrary-file-write-via-output-path-symlink-and-toctou
