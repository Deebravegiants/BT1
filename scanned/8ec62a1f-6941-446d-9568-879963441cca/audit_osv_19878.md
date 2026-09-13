# [H] CVE-2021-27229

## Summary
Severity: High
Advisory: CVE-2021-27229
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-02-16
Source: https://osv.dev/vulnerability/CVE-2021-27229
Type: osv

## Details
Mumble before 1.3.4 allows remote code execution if a victim navigates to a crafted URL on a server list and clicks on the Open Webpage text.

## References
- https://lists.debian.org/debian-lts-announce/2021/02/msg00022.html
- https://security.gentoo.org/glsa/202105-13
- https://github.com/mumble-voip/mumble/commit/e59ee87abe249f345908c7d568f6879d16bfd648
- https://github.com/mumble-voip/mumble/compare/1.3.3...1.3.4
- https://github.com/mumble-voip/mumble/pull/4733
