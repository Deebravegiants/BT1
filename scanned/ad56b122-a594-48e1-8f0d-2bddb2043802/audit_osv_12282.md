# [H] CVE-2018-1122

## Summary
Severity: High
Advisory: CVE-2018-1122
CVSS: 7.0 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-23
Source: https://osv.dev/vulnerability/CVE-2018-1122
Type: osv

## Details
procps-ng before version 3.3.15 is vulnerable to a local privilege escalation in top. If a user runs top with HOME unset in an attacker-controlled directory, the attacker could achieve privilege escalation by exploiting one of several vulnerabilities in the config_file() function.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00058.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00059.html
- http://seclists.org/oss-sec/2018/q2/122
- http://www.securityfocus.com/bid/104214
- https://access.redhat.com/errata/RHSA-2019:2189
- https://access.redhat.com/errata/RHSA-2020:0595
- https://lists.debian.org/debian-lts-announce/2018/05/msg00021.html
- https://security.gentoo.org/glsa/201805-14
- https://usn.ubuntu.com/3658-1/
- https://usn.ubuntu.com/3658-3/
- https://www.debian.org/security/2018/dsa-4208
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-1122
- https://www.exploit-db.com/exploits/44806/
- https://www.qualys.com/2018/05/17/procps-ng-audit-report-advisory.txt
