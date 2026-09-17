# [H] OpenEMR has Session Timeout Bypass via skip_timeout_reset

## Summary
Severity: High
Advisory: CVE-2026-25476
Aliases: GHSA-gx7q-6fhr-5h33
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-25476
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to version 8.0.0, the session expiration check in `library/auth.inc.php` runs only when `skip_timeout_reset` is not present in the request. When `skip_timeout_reset=1` is sent, the entire block that calls `SessionTracker::isSessionExpired()` and forces logout on timeout is skipped. As a result, any request that includes this parameter (e.g. from auto-refresh pages like the Patient Flow Board) never runs the expiration check: expired sessions can continue to access data indefinitely, abandoned workstations stay active, and an attacker with a stolen session cookie can keep sending `skip_timeout_reset=1` to avoid being logged out. Version 8.0.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25476.json
- https://github.com/openemr/openemr/security/advisories/GHSA-gx7q-6fhr-5h33
- https://nvd.nist.gov/vuln/detail/CVE-2026-25476
- https://github.com/openemr/openemr/commit/02a6a7793402b10356a94626d78e0e1069e92a77
