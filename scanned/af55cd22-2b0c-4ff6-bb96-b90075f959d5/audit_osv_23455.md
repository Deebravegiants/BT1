# [H] CVE-2022-4883

## Summary
Severity: High
Advisory: CVE-2022-4883
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-02-07
Source: https://osv.dev/vulnerability/CVE-2022-4883
Type: osv

## Details
A flaw was found in libXpm. When processing files with .Z or .gz extensions, the library calls external programs to compress and uncompress files, relying on the PATH environment variable to find these programs, which could allow a malicious user to execute other programs by manipulating the PATH environment variable.

## References
- https://lists.x.org/archives/xorg-announce/2023-January/003312.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/4xxx/CVE-2022-4883.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-4883
- https://bugzilla.redhat.com/show_bug.cgi?id=2160213
- https://gitlab.freedesktop.org/xorg/lib/libxpm/-/commit/515294bb8023a45ff91669
- https://gitlab.freedesktop.org/xorg/lib/libxpm/-/merge_requests/9
- https://lists.debian.org/debian-lts-announce/2023/06/msg00021.html
