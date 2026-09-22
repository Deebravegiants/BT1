# [H] RELATE: Predictable Token Generation in auth.py and exam.py

## Summary
Severity: High
Advisory: CVE-2026-41505
Aliases: GHSA-rvx5-95mm-p77v
CVSS: 8.7 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:H/A:H)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/CVE-2026-41505
Type: osv

## Details
RELATE is a web-based courseware package. Prior to commit 2f68e16, RELATE is vulnerable to predictable token generation in auth.py's make_sign_in_key() function and exam.py's gen_ticket_code() function. This issue has been patched via commit 2f68e16.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41505.json
- https://github.com/inducer/relate/security/advisories/GHSA-rvx5-95mm-p77v
- https://nvd.nist.gov/vuln/detail/CVE-2026-41505
- https://github.com/inducer/relate/commit/2f68e16cd3b96d25c188c1aa3f7e13cdb15cdaeb
