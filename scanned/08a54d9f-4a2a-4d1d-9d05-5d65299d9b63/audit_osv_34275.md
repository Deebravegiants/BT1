# [H] CVE-2025-57328

## Summary
Severity: High
Advisory: CVE-2025-57328
Aliases: GHSA-34q3-8x9v-j957
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-24
Source: https://osv.dev/vulnerability/CVE-2025-57328
Type: osv

## Details
toggle-array is a package designed to enables a property on the object at the specified index, while disabling the property on all other objects. A Prototype Pollution vulnerability in the enable and disable function of toggle-array v1.0.1 and before allows attackers to inject properties on Object.prototype via supplying a crafted payload, causing denial of service (DoS) as the minimum consequence.

## References
- https://github.com/VulnSageAgent/PoCs/blob/main/JavaScript/prototype-pollution/toggle-array%401.0.1/index.js
- https://github.com/VulnSageAgent/PoCs/tree/main/JavaScript/prototype-pollution/CVE-2025-57328
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57328.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-57328
