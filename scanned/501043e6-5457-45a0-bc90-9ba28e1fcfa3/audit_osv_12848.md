# [H] CVE-2018-15686

## Summary
Severity: High
Advisory: CVE-2018-15686
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-26
Source: https://osv.dev/vulnerability/CVE-2018-15686
Type: osv

## Details
A vulnerability in unit_deserialize of systemd allows an attacker to supply arbitrary state across systemd re-execution via NotifyAccess. This can be used to improperly influence systemd execution and possibly lead to root privilege escalation. Affected releases are systemd versions up to and including 239.

## References
- https://lists.apache.org/thread.html/r1b103833cb5bc8466e24ff0ecc5e75b45a705334ab6a444e64e840a0%40%3Cissues.bookkeeper.apache.org%3E
- http://www.securityfocus.com/bid/105747
- https://access.redhat.com/errata/RHSA-2019:2091
- https://access.redhat.com/errata/RHSA-2019:3222
- https://access.redhat.com/errata/RHSA-2020:0593
- https://lists.debian.org/debian-lts-announce/2018/11/msg00017.html
- https://security.gentoo.org/glsa/201810-10
- https://usn.ubuntu.com/3816-1/
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://github.com/systemd/systemd/pull/10519
- https://www.exploit-db.com/exploits/45714/
