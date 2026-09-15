# [C] BIT-golang-2021-38297

## Summary
Severity: Critical
Advisory: BIT-golang-2021-38297
Aliases: CVE-2021-38297, GO-2022-0247
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2021-38297
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.17.0 <1.17.2

## Details
Go before 1.16.9 and 1.17.x before 1.17.2 has a Buffer Overflow via large arguments in a function invocation from a WASM module, when GOARCH=wasm GOOS=js is used.

## References
- https://groups.google.com/forum/#%21forum/golang-announce
- https://groups.google.com/g/golang-announce/c/AEBu9j7yj5A
- https://lists.debian.org/debian-lts-announce/2023/04/msg00021.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4OFS3M3OFB24SWPTIAPARKGPUMQVUY6Z/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ON7BQRRJZBOR5TJHURBAB3WLF4YXFC6Z/
- https://security.gentoo.org/glsa/202208-02
- https://security.netapp.com/advisory/ntap-20211118-0006/
- https://nvd.nist.gov/vuln/detail/CVE-2021-38297
