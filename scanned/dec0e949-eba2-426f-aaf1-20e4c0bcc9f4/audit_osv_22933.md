# [H] CVE-2022-41322

## Summary
Severity: High
Advisory: CVE-2022-41322
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-09-23
Source: https://osv.dev/vulnerability/CVE-2022-41322
Type: osv

## Details
In Kitty before 0.26.2, insufficient validation in the desktop notification escape sequence can lead to arbitrary code execution. The user must display attacker-controlled content in the terminal, then click on a notification popup.

## References
- https://bugs.gentoo.org/868543
- https://github.com/kovidgoyal/kitty/compare/v0.26.1...v0.26.2
- https://lists.debian.org/debian-lts-announce/2025/06/msg00000.html
- https://sw.kovidgoyal.net/kitty/changelog/#detailed-list-of-changes
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41322.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/47RK7MBSVY5BWDUTYMJUFPBAYFSWMTOI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6RRNAPU33PHEH64P77YL3AJO6CTZGHTX/
- https://nvd.nist.gov/vuln/detail/CVE-2022-41322
- https://security.gentoo.org/glsa/202209-22
- https://github.com/kovidgoyal/kitty/commit/f05783e64d5fa62e1aed603e8d69aced5e49824f
