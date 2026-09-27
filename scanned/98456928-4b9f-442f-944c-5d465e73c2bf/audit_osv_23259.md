# [H] CVE-2022-46285

## Summary
Severity: High
Advisory: CVE-2022-46285
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-07
Source: https://osv.dev/vulnerability/CVE-2022-46285
Type: osv

## Details
A flaw was found in libXpm. This issue occurs when parsing a file with a comment not closed; the end-of-file condition will not be detected, leading to an infinite loop and resulting in a Denial of Service in the application linked to the library.

## References
- https://lists.x.org/archives/xorg-announce/2023-January/003312.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/46xxx/CVE-2022-46285.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-46285
- https://bugzilla.redhat.com/show_bug.cgi?id=2160092
- https://gitlab.freedesktop.org/xorg/lib/libxpm/-/commit/a3a7c6dcc3b629d7650148
- https://gitlab.freedesktop.org/xorg/lib/libxpm/-/merge_requests/9
- http://www.openwall.com/lists/oss-security/2023/10/03/1
- http://www.openwall.com/lists/oss-security/2023/10/03/10
- https://lists.debian.org/debian-lts-announce/2023/06/msg00021.html
