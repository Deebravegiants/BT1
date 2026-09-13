# [C] CVE-2018-17456

## Summary
Severity: Critical
Advisory: CVE-2018-17456
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-06
Source: https://osv.dev/vulnerability/CVE-2018-17456
Type: osv

## Details
Git before 2.14.5, 2.15.x before 2.15.3, 2.16.x before 2.16.5, 2.17.x before 2.17.2, 2.18.x before 2.18.1, and 2.19.x before 2.19.1 allows remote code execution during processing of a recursive "git clone" of a superproject if a .gitmodules file has a URL field beginning with a '-' character.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00003.html
- http://packetstormsecurity.com/files/152173/Sourcetree-Git-Arbitrary-Code-Execution-URL-Handling.html
- http://www.securityfocus.com/bid/105523
- http://www.securityfocus.com/bid/107511
- http://www.securitytracker.com/id/1041811
- https://access.redhat.com/errata/RHSA-2018:3408
- https://access.redhat.com/errata/RHSA-2018:3505
- https://access.redhat.com/errata/RHSA-2018:3541
- https://access.redhat.com/errata/RHSA-2020:0316
- https://marc.info/?l=git&m=153875888916397&w=2
- https://seclists.org/bugtraq/2019/Mar/30
- https://usn.ubuntu.com/3791-1/
- https://www.debian.org/security/2018/dsa-4311
- https://www.openwall.com/lists/oss-security/2018/10/06/3
- https://github.com/git/git/commit/1a7fd1fb2998002da6e9ff2ee46e1bdd25ee8404
- https://github.com/git/git/commit/a124133e1e6ab5c7a9fef6d0e6bcb084e3455b46
- https://www.exploit-db.com/exploits/45548/
- https://www.exploit-db.com/exploits/45631/
