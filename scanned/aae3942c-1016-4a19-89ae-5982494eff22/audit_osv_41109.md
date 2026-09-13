# [M] CVE-2026-57825

## Summary
Severity: Medium
Advisory: CVE-2026-57825
Aliases: OSEC-2026-10
CVSS: 5.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-57825
Type: osv

## Details
In the opam package before 2.5.2 for OCaml, the sandbox protection mechanism can be bypassed because symlinks are mishandled during use of .install files.

## References
- https://lists.debian.org/debian-lts-announce/2026/07/msg00026.html
- https://osv.dev/vulnerability/OSEC-2026-10
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57825.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-57825
- https://github.com/ocaml/opam/releases
