# [H] BIT-golang-2021-33196

## Summary
Severity: High
Advisory: BIT-golang-2021-33196
Aliases: CVE-2021-33196, GO-2021-0240
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2021-33196
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.16.0 <1.16.5

## Details
In archive/zip in Go before 1.15.13 and 1.16.x before 1.16.5, a crafted file count (in an archive's header) can cause a NewReader or OpenReader panic.

## References
- https://groups.google.com/g/golang-announce
- https://groups.google.com/g/golang-announce/c/RgCMkAEQjSI
- https://lists.debian.org/debian-lts-announce/2022/01/msg00016.html
- https://lists.debian.org/debian-lts-announce/2022/01/msg00017.html
- https://lists.debian.org/debian-lts-announce/2023/04/msg00021.html
- https://security.gentoo.org/glsa/202208-02
- https://nvd.nist.gov/vuln/detail/CVE-2021-33196
