# [M] CVE-2023-29576

## Summary
Severity: Medium
Advisory: CVE-2023-29576
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-04-11
Source: https://osv.dev/vulnerability/CVE-2023-29576
Type: osv

## Details
Bento4 v1.6.0-639 was discovered to contain a segmentation violation via the AP4_TrunAtom::SetDataOffset(int) function in Ap4TrunAtom.h.

## References
- https://github.com/z1r00/fuzz_vuln/blob/main/Bento4/mp4decrypt/sigv/readme.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/29xxx/CVE-2023-29576.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-29576
- https://github.com/axiomatic-systems/Bento4/issues/844
