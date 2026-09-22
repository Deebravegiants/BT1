# [H] CVE-2019-25051

## Summary
Severity: High
Advisory: CVE-2019-25051
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-07-20
Source: https://osv.dev/vulnerability/CVE-2019-25051
Type: osv

## Details
objstack in GNU Aspell 0.60.8 has a heap-based buffer overflow in acommon::ObjStack::dup_top (called from acommon::StringMap::add and acommon::Config::lookup_list).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/H7E4EI7F6TVN7K6XWU6HSANMCOKKEREE/
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=18462
- https://github.com/google/oss-fuzz-vulns/blob/main/vulns/aspell/OSV-2020-521.yaml
- https://lists.debian.org/debian-lts-announce/2021/07/msg00021.html
- https://www.debian.org/security/2021/dsa-4948
- https://github.com/gnuaspell/aspell/commit/0718b375425aad8e54e1150313b862e4c6fd324a
