# [H] CVE-2025-57326

## Summary
Severity: High
Advisory: CVE-2025-57326
Aliases: GHSA-3mpm-jx38-9m8w
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-24
Source: https://osv.dev/vulnerability/CVE-2025-57326
Type: osv

## Details
A Prototype Pollution vulnerability in the byGroupAndType function of sassdoc-extras v2.5.1 and before allows attackers to inject properties on Object.prototype via supplying a crafted payload, causing denial of service (DoS) as the minimum consequence.

## References
- https://github.com/VulnSageAgent/PoCs/blob/main/JavaScript/prototype-pollution/sassdoc-extras%402.5.1/index.js
- https://github.com/VulnSageAgent/PoCs/tree/main/JavaScript/prototype-pollution/CVE-2025-57326
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57326.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-57326
