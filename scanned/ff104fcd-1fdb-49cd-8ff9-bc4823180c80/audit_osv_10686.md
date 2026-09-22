# [M] CVE-2017-18248

## Summary
Severity: Medium
Advisory: CVE-2017-18248
CVSS: 5.3 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-26
Source: https://osv.dev/vulnerability/CVE-2017-18248
Type: osv

## Details
The add_job function in scheduler/ipp.c in CUPS before 2.2.6, when D-Bus support is enabled, can be crashed by remote attackers by sending print jobs with an invalid username, related to a D-Bus notification.

## References
- https://lists.debian.org/debian-lts-announce/2018/05/msg00018.html
- https://lists.debian.org/debian-lts-announce/2018/07/msg00003.html
- https://usn.ubuntu.com/3713-1/
- https://github.com/apple/cups/releases/tag/v2.2.6
- https://github.com/apple/cups/commit/49fa4983f25b64ec29d548ffa3b9782426007df3
- https://github.com/apple/cups/issues/5143
- https://security.cucumberlinux.com/security/details.php?id=346
