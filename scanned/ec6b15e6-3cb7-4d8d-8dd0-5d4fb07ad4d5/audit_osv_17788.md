# [M] CVE-2020-19721

## Summary
Severity: Medium
Advisory: CVE-2020-19721
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-07-13
Source: https://osv.dev/vulnerability/CVE-2020-19721
Type: osv

## Details
A heap buffer overflow vulnerability in Ap4TrunAtom.cpp of Bento 1.5.1-628 may lead to an out-of-bounds write while running mp42aac, leading to system crashes and a denial of service (DOS).

## References
- https://cwe.mitre.org/data/definitions/122.html
- https://github.com/axiomatic-systems/Bento4/issues/415
