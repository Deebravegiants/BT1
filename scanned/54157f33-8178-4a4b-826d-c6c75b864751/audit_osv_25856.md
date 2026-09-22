# [M] jumpserver is vulnerable to password brute-force protection bypass via arbitrary IP values

## Summary
Severity: Medium
Advisory: CVE-2023-46123
Aliases: GHSA-hvw4-766m-p89f
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-10-25
Source: https://osv.dev/vulnerability/CVE-2023-46123
Type: osv

## Details
jumpserver is an open source bastion machine, professional operation and maintenance security audit system that complies with 4A specifications. A flaw in the Core API allows attackers to bypass password brute-force protections by spoofing arbitrary IP addresses. By exploiting this vulnerability, attackers can effectively make unlimited password attempts by altering their apparent IP address for each request. This vulnerability has been patched in version 3.8.0.

## References
- https://github.com/jumpserver/jumpserver/releases/tag/v3.8.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/46xxx/CVE-2023-46123.json
- https://github.com/jumpserver/jumpserver/security/advisories/GHSA-hvw4-766m-p89f
- https://nvd.nist.gov/vuln/detail/CVE-2023-46123
- https://www.sonarsource.com/blog/diving-into-jumpserver-attackers-gateway-to-internal-networks-1-2
