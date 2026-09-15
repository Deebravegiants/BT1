# [H] ToolJet - Token Leakage via Referer Header

## Summary
Severity: High
Advisory: CVE-2022-23067
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-05-18
Source: https://osv.dev/vulnerability/CVE-2022-23067
Type: osv

## Details
ToolJet versions v0.5.0 to v1.2.2 are vulnerable to token leakage via Referer header that leads to account takeover . If the user opens the invite link/signup link and then clicks on any external links within the page, it leaks the password set token/signup token in the referer header. Using these tokens the attacker can access the user’s account.

## References
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2022-23067
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23067.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-23067
- https://github.com/ToolJet/ToolJet/commit/eacbfc4c9da089ff9cda9edf8a1156390ae8a101
