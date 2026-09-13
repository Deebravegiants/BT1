# [M] CVE-2022-43033

## Summary
Severity: Medium
Advisory: CVE-2022-43033
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-10-19
Source: https://osv.dev/vulnerability/CVE-2022-43033
Type: osv

## Details
An issue was discovered in Bento4 1.6.0-639. There is a bad free in the component AP4_HdlrAtom::~AP4_HdlrAtom() which allows attackers to cause a Denial of Service (DoS) via a crafted input.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/43xxx/CVE-2022-43033.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-43033
- https://github.com/axiomatic-systems/Bento4/issues/765
