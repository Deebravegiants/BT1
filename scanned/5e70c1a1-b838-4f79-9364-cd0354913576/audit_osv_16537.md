# [M] CVE-2019-7697

## Summary
Severity: Medium
Advisory: CVE-2019-7697
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-02-10
Source: https://osv.dev/vulnerability/CVE-2019-7697
Type: osv

## Details
An issue was discovered in Bento4 v1.5.1-627. There is an assertion failure in AP4_AtomListWriter::Action in Core/Ap4Atom.cpp, leading to a denial of service (program crash), as demonstrated by mp42hls.

## References
- https://github.com/axiomatic-systems/Bento4/issues/351
