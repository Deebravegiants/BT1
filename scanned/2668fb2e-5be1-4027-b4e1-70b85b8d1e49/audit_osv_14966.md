# [H] CVE-2019-12735

## Summary
Severity: High
Advisory: CVE-2019-12735
CVSS: 8.6 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2019-06-05
Source: https://osv.dev/vulnerability/CVE-2019-12735
Type: osv

## Details
getchar.c in Vim before 8.1.1365 and Neovim before 0.3.6 allows remote attackers to execute arbitrary OS commands via the :source! command in a modeline, as demonstrated by execute in Vim, and assert_fails or nvim_input in Neovim.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00031.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00036.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00037.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00034.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00050.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00075.html
- http://www.securityfocus.com/bid/108724
- https://lists.debian.org/debian-lts-announce/2019/08/msg00003.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2BMDSHTF754TITC6AQJPCS5IRIDMMIM7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TRIRBC2YRGKPAWVRMZS4SZTGGCVRVZPR/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2BMDSHTF754TITC6AQJPCS5IRIDMMIM7/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TRIRBC2YRGKPAWVRMZS4SZTGGCVRVZPR/
- https://seclists.org/bugtraq/2019/Jul/39
- https://seclists.org/bugtraq/2019/Jun/33
- https://support.f5.com/csp/article/K93144355
- https://support.f5.com/csp/article/K93144355?utm_source=f5support&amp%3Butm_medium=RSS
- https://support.f5.com/csp/article/K93144355?utm_source=f5support&amp;utm_medium=RSS
- https://usn.ubuntu.com/4016-1/
- https://usn.ubuntu.com/4016-2/
- https://www.exploit-db.com/exploits/46973
