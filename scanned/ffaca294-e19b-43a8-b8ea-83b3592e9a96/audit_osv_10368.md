# [M] CVE-2017-15130

## Summary
Severity: Medium
Advisory: CVE-2017-15130
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-02
Source: https://osv.dev/vulnerability/CVE-2017-15130
Type: osv

## Details
A denial of service flaw was found in dovecot before 2.2.34. An attacker able to generate random SNI server names could exploit TLS SNI configuration lookups, leading to excessive memory usage and the process to restart.

## References
- https://lists.debian.org/debian-lts-announce/2018/03/msg00036.html
- https://usn.ubuntu.com/3587-2/
- http://seclists.org/oss-sec/2018/q1/205
- https://usn.ubuntu.com/3587-1/
- https://www.debian.org/security/2018/dsa-4130
- https://www.dovecot.org/list/dovecot-news/2018-February/000370.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1532356
