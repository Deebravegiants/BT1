# [H] CVE-2017-18266

## Summary
Severity: High
Advisory: CVE-2017-18266
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-05-10
Source: https://osv.dev/vulnerability/CVE-2017-18266
Type: osv

## Details
The open_envvar function in xdg-open in xdg-utils before 1.1.3 does not validate strings before launching the program specified by the BROWSER environment variable, which might allow remote attackers to conduct argument-injection attacks via a crafted URL, as demonstrated by %s in this environment variable.

## References
- https://cgit.freedesktop.org/xdg/xdg-utils/commit/?id=5647afb35e4bcba2060148e1a2a47bc43cc240f2
- https://cgit.freedesktop.org/xdg/xdg-utils/tree/ChangeLog
- https://lists.debian.org/debian-lts-announce/2018/05/msg00014.html
- https://usn.ubuntu.com/3650-1/
- https://www.debian.org/security/2018/dsa-4211
- https://bugs.freedesktop.org/show_bug.cgi?id=103807
- https://cgit.freedesktop.org/xdg/xdg-utils/commit/?id=ce802d71c3466d1dbb24f2fe9b6db82a1f899bcb
