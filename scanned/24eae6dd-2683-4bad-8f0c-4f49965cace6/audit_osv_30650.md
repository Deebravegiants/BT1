# [M] Arbitrary file download in Zoo-Project Echo Example

## Summary
Severity: Medium
Advisory: CVE-2024-53982
Aliases: GHSA-93rv-45r8-h5j4
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2024-12-04
Source: https://osv.dev/vulnerability/CVE-2024-53982
Type: osv

## Details
ZOO-Project is a C-based WPS (Web Processing Service) implementation. A path traversal vulnerability was discovered in Zoo-Project Echo example. The Echo example available by default in Zoo installs implements file caching, which can be controlled by user-given parameters. No input validation is performed in this parameter, which allows an attacker to fully control the file which is returned in the response. Patch was committed in November 22nd, 2024.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53982.json
- https://github.com/ZOO-Project/ZOO-Project/security/advisories/GHSA-93rv-45r8-h5j4
- https://nvd.nist.gov/vuln/detail/CVE-2024-53982
- https://github.com/ZOO-Project/ZOO-Project/commit/641cb18fec58de43a3468f314e5f8808c560e6d9
