# [H] CVE-2025-59375

## Summary
Severity: High
Advisory: CVE-2025-59375
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H/E:H/RL:T/RC:C)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2025-59375
Type: osv

## Details
libexpat in Expat before 2.7.2 allows attackers to trigger large dynamic memory allocations via a small document that is submitted for parsing.

## References
- http://www.openwall.com/lists/oss-security/2025/09/16/2
- http://www.openwall.com/lists/oss-security/2026/05/01/5
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://cert-portal.siemens.com/productcert/html/ssa-089022.html
- https://github.com/libexpat/libexpat/blob/676a4c531ec768732fac215da9730b5f50fbd2bf/expat/Changes#L45-L74
- https://github.com/libexpat/libexpat/blob/R_2_7_2/expat/Changes
- https://issues.oss-fuzz.com/issues/439133977
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59375.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-59375
- https://github.com/libexpat/libexpat/issues/1018
- https://github.com/libexpat/libexpat/pull/1034
