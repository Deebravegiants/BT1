# [C] CVE-2025-57347

## Summary
Severity: Critical
Advisory: CVE-2025-57347
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-24
Source: https://osv.dev/vulnerability/CVE-2025-57347
Type: osv

## Details
A vulnerability exists in the 'dagre-d3-es' Node.js package version 7.0.9, specifically within the 'bk' module's addConflict function, which fails to properly sanitize user-supplied input during property assignment operations. This flaw allows attackers to exploit prototype pollution vulnerabilities by injecting malicious input values (e.g., "__proto__"), enabling unauthorized modification of the JavaScript Object prototype chain. Successful exploitation could lead to denial of service conditions, unexpected application behavior, or potential execution of arbitrary code in contexts where polluted properties are later accessed or executed. The issue affects versions prior to 7.0.11 and remains unpatched at the time of disclosure.

## References
- https://github.com/VulnSageAgent/PoCs/tree/main/JavaScript/prototype-pollution/CVE-2025-57347
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57347.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-57347
- https://github.com/tbo47/dagre-es/issues/52
