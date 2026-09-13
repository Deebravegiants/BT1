# [M] DataEase: Hardcoded JWT Signing Secret in ShareLink

## Summary
Severity: Medium
Advisory: CVE-2026-57172
Aliases: GHSA-7cpg-f4cj-7pgm
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-57172
Type: osv

## Details
DataEase is an open source data visualization and analysis tool. Prior to 2.10.24, ShareSecretManage uses a hardcoded default share link signature key, allowing an attacker who can obtain a passwordless share for a resource and user to use the known key link-pwd-fit2cloud to forge linkToken JWTs, bypass TokenFilter verification, and access backend resources as the share creator even if the original share has been revoked. This issue is fixed in version 2.10.24.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57172.json
- https://github.com/dataease/dataease/security/advisories/GHSA-7cpg-f4cj-7pgm
- https://nvd.nist.gov/vuln/detail/CVE-2026-57172
- https://github.com/dataease/dataease/commit/356e83b518603f5612104760ced80aae8fc5d675
