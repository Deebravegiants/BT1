# [H] CVE-2025-57325

## Summary
Severity: High
Advisory: CVE-2025-57325
Aliases: GHSA-r8c2-2qwq-94p6
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-24
Source: https://osv.dev/vulnerability/CVE-2025-57325
Type: osv

## Details
rollbar is a package designed to effortlessly track and debug errors in JavaScript applications. This package includes advanced error tracking features and an intuitive interface to help you identify and fix issues more quickly. A Prototype Pollution vulnerability in the utility.set function of rollbar v2.26.4 and before allows attackers to inject properties on Object.prototype via supplying a crafted payload, causing denial of service (DoS) as the minimum consequence.

## References
- https://github.com/VulnSageAgent/PoCs/blob/main/JavaScript/prototype-pollution/rollbar%402.26.4/index.js
- https://github.com/VulnSageAgent/PoCs/tree/main/JavaScript/prototype-pollution/CVE-2025-57325
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57325.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-57325
