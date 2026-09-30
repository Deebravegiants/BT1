# [H] CVE-2025-57327

## Summary
Severity: High
Advisory: CVE-2025-57327
Aliases: GHSA-r2rv-8pp3-65xw
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-24
Source: https://osv.dev/vulnerability/CVE-2025-57327
Type: osv

## Details
spmrc is a package that provides the rc manager for spm. A Prototype Pollution vulnerability in the set and config function of spmrc version 1.2.0 and before allows attackers to inject properties on Object.prototype via supplying a crafted payload, causing denial of service (DoS) as the minimum consequence.

## References
- https://github.com/VulnSageAgent/PoCs/blob/main/JavaScript/prototype-pollution/spmrc%401.2.0/index.js
- https://github.com/VulnSageAgent/PoCs/tree/main/JavaScript/prototype-pollution/CVE-2025-57327
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57327.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-57327
