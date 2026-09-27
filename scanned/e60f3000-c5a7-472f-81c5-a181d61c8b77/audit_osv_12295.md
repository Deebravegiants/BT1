# [H] CVE-2018-1125

## Summary
Severity: High
Advisory: CVE-2018-1125
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-05-23
Source: https://osv.dev/vulnerability/CVE-2018-1125
Type: osv

## Details
procps-ng before version 3.3.15 is vulnerable to a stack buffer overflow in pgrep. This vulnerability is mitigated by FORTIFY, as it involves strncat() to a stack-allocated string. When pgrep is compiled with FORTIFY (as on Red Hat Enterprise Linux and Fedora), the impact is limited to a crash.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00058.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00059.html
- http://seclists.org/oss-sec/2018/q2/122
- http://www.securityfocus.com/bid/104214
- https://lists.debian.org/debian-lts-announce/2018/05/msg00021.html
- https://usn.ubuntu.com/3658-1/
- https://usn.ubuntu.com/3658-3/
- https://www.debian.org/security/2018/dsa-4208
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-1125
- https://www.qualys.com/2018/05/17/procps-ng-audit-report-advisory.txt
