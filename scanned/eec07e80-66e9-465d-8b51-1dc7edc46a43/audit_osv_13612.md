# [H] CVE-2018-20506

## Summary
Severity: High
Advisory: CVE-2018-20506
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-03
Source: https://osv.dev/vulnerability/CVE-2018-20506
Type: osv

## Details
SQLite before 3.25.3, when the FTS3 extension is enabled, encounters an integer overflow (and resultant buffer overflow) for FTS3 queries in a "merge" operation that occurs after crafted changes to FTS3 shadow tables, allowing remote attackers to execute arbitrary code by leveraging the ability to run arbitrary SQL statements (such as in certain WebSQL use cases). This is a different vulnerability than CVE-2018-20346.

## References
- https://kc.mcafee.com/corporate/index?page=content&id=SB10365
- https://lists.debian.org/debian-lts-announce/2020/08/msg00037.html
- https://usn.ubuntu.com/4019-1/
- https://usn.ubuntu.com/4019-2/
- https://www.oracle.com/security-alerts/cpuapr2020.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00070.html
- http://seclists.org/fulldisclosure/2019/Jan/62
- http://seclists.org/fulldisclosure/2019/Jan/64
- http://seclists.org/fulldisclosure/2019/Jan/66
- http://seclists.org/fulldisclosure/2019/Jan/67
- http://seclists.org/fulldisclosure/2019/Jan/68
- http://seclists.org/fulldisclosure/2019/Jan/69
- http://www.securityfocus.com/bid/106698
- https://seclists.org/bugtraq/2019/Jan/28
- https://seclists.org/bugtraq/2019/Jan/29
- https://seclists.org/bugtraq/2019/Jan/31
- https://seclists.org/bugtraq/2019/Jan/32
- https://seclists.org/bugtraq/2019/Jan/33
- https://seclists.org/bugtraq/2019/Jan/39
- https://security.netapp.com/advisory/ntap-20190502-0004/
