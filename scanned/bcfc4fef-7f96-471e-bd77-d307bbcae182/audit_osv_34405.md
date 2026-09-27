# [H] The Scratch Channel forks can publish articles

## Summary
Severity: High
Advisory: CVE-2025-59416
Aliases: GHSA-775w-g375-pjff
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:H/SC:H/SI:N/SA:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2025-59416
Type: osv

## Details
The Scratch Channel is a news website. If the user makes a fork, they can change the admins and make an article. Since the API uses a POST request, it will make an article. This issue is fixed in v1.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59416.json
- https://github.com/The-Scratch-Channel/tsc-web-client/security/advisories/GHSA-775w-g375-pjff
- https://nvd.nist.gov/vuln/detail/CVE-2025-59416
