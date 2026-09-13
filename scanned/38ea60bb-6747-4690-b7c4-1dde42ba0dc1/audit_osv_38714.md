# [C] RELATE: Timing Attack Vulnerability in course/auth.py — check_sign_in_key()

## Summary
Severity: Critical
Advisory: CVE-2026-41588
Aliases: GHSA-78j7-9xr9-2728
CVSS: 9.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-41588
Type: osv

## Details
RELATE is a web-based courseware package. Prior to commit 2f68e16, there is a timing attack vulnerability in course/auth.py — check_sign_in_key(). This issue has been patched via commit 2f68e16.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41588.json
- https://github.com/inducer/relate/security/advisories/GHSA-78j7-9xr9-2728
- https://nvd.nist.gov/vuln/detail/CVE-2026-41588
- https://github.com/inducer/relate/commit/2f68e16cd3b96d25c188c1aa3f7e13cdb15cdaeb
