# [H] CVE-2023-32700

## Summary
Severity: High
Advisory: CVE-2023-32700
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-05-20
Source: https://osv.dev/vulnerability/CVE-2023-32700
Type: osv

## Details
LuaTeX before 1.17.0 allows execution of arbitrary shell commands when compiling a TeX file obtained from an untrusted source. This occurs because luatex-core.lua lets the original io.popen be accessed. This also affects TeX Live before 2023 r66984 and MiKTeX before 23.5.

## References
- https://github.com/TeX-Live/texlive-source/releases/tag/build-svn66984
- https://gitlab.lisn.upsaclay.fr/texlive/luatex/-/tags/1.17.0
- https://tug.org/pipermail/tex-live/2023-May/049188.html
- https://tug.org/~mseven/luatex.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32700.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RLY43MIRONJSJVNBDFQHQ26MP3JIOB3H/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TF6YXUUFRGBIXIIIEV5SGBJXXT2SMUK5/
- https://nvd.nist.gov/vuln/detail/CVE-2023-32700
