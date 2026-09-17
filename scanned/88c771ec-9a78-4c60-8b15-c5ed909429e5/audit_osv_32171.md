# [H] Incorrect input validation could allow an authenticated user to read sensitive information

## Summary
Severity: High
Advisory: CVE-2025-25206
Aliases: GHSA-qffc-rfjh-77gg
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2025-02-14
Source: https://osv.dev/vulnerability/CVE-2025-25206
Type: osv

## Details
eLabFTW is an open source electronic lab notebook for research labs. Prior to version 5.1.15, an incorrect input validation could allow an authenticated user to read sensitive information, including login token or other content stored in the database. This could lead to privilege escalation if cookies are enabled (default setting). Users must upgrade to eLabFTW version 5.1.15 to receive a fix. No known workarounds are available.

## References
- https://github.com/elabftw/elabftw/releases/tag/5.1.15
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/25xxx/CVE-2025-25206.json
- https://github.com/elabftw/elabftw/security/advisories/GHSA-qffc-rfjh-77gg
- https://nvd.nist.gov/vuln/detail/CVE-2025-25206
