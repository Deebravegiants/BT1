# [H] CVE-2022-44617

## Summary
Severity: High
Advisory: CVE-2022-44617
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-06
Source: https://osv.dev/vulnerability/CVE-2022-44617
Type: osv

## Details
A flaw was found in libXpm. When processing a file with width of 0 and a very large height, some parser functions will be called repeatedly and can lead to an infinite loop, resulting in a Denial of Service in the application linked to the library.

## References
- https://lists.x.org/archives/xorg-announce/2023-January/003312.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/44xxx/CVE-2022-44617.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-44617
- https://bugzilla.redhat.com/show_bug.cgi?id=2160193
- https://gitlab.freedesktop.org/xorg/lib/libxpm/-/commit/f80fa6ae47ad4a5beacb28
- https://gitlab.freedesktop.org/xorg/lib/libxpm/-/merge_requests/9
- https://lists.debian.org/debian-lts-announce/2023/06/msg00021.html
