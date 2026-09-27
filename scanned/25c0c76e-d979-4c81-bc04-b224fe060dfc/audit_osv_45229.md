# [M] libarchive 3.4.1 through 3.5.1 has a use-after-free in `copy_string` (called from...

## Summary
Severity: Medium
Advisory: JLSEC-2025-234
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-234
Type: osv

## Affected
- Julia: `LibArchive_jll` — affected >=0 <3.7.4+0

## Details
libarchive 3.4.1 through 3.5.1 has a use-after-free in `copy_string` (called from `do_uncompress_block` and `process_block`).

## References
- http://seclists.org/fulldisclosure/2022/Mar/27
- http://seclists.org/fulldisclosure/2022/Mar/28
- http://seclists.org/fulldisclosure/2022/Mar/29
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=32375
- https://github.com/google/oss-fuzz-vulns/blob/main/vulns/libarchive/OSV-2021-557.yaml
- https://lists.debian.org/debian-lts-announce/2024/11/msg00007.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SE5NJQNM22ZE5Z55LPAGCUHSBQZBKMKC/
- https://security.gentoo.org/glsa/202208-26
- https://support.apple.com/kb/HT213182
- https://support.apple.com/kb/HT213183
- https://support.apple.com/kb/HT213193
