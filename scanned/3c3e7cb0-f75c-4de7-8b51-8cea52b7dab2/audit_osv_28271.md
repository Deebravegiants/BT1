# [M] CVE-2024-30806

## Summary
Severity: Medium
Advisory: CVE-2024-30806
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-04-02
Source: https://osv.dev/vulnerability/CVE-2024-30806
Type: osv

## Details
An issue was discovered in Bento4 v1.6.0-641-2-g1529b83. There is a heap overflow in AP4_Dec3Atom::AP4_Dec3Atom at Ap4Dec3Atom.cpp, leading to a Denial of Service (DoS), as demonstrated by mp42aac.

## References
- https://github.com/zhangteng0526/CVE-information/blob/main/CVE-2024-30806
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/30xxx/CVE-2024-30806.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-30806
- https://github.com/axiomatic-systems/Bento4/issues/914
