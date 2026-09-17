# [M] CVE-2023-32668

## Summary
Severity: Medium
Advisory: CVE-2023-32668
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2023-05-11
Source: https://osv.dev/vulnerability/CVE-2023-32668
Type: osv

## Details
LuaTeX before 1.17.0 allows a document (compiled with the default settings) to make arbitrary network requests. This occurs because full access to the socket library is permitted by default, as stated in the documentation. This also affects TeX Live before 2023 r66984 and MiKTeX before 23.5.

## References
- https://gitlab.lisn.upsaclay.fr/texlive/luatex/-/blob/b266ef076c96b382cd23a4c93204e247bb98626a/source/texk/web2c/luatexdir/ChangeLog#L1-L3
- https://gitlab.lisn.upsaclay.fr/texlive/luatex/-/tags/1.17.0
- https://lists.debian.org/debian-lts-announce/2024/10/msg00032.html
- https://tug.org/pipermail/tex-live/2023-May/049188.html
- https://tug.org/~mseven/luatex.html#luasocket
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32668.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-32668
