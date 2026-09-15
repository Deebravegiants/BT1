# [H] CVE-2017-7466

## Summary
Severity: High
Advisory: CVE-2017-7466
Aliases: GHSA-3m8p-xpm6-8ww3, PYSEC-2018-40
CVSS: 8.0 (CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-06-22
Source: https://osv.dev/vulnerability/CVE-2017-7466
Type: osv

## Details
Ansible before version 2.3 has an input validation vulnerability in the handling of data sent from client systems. An attacker with control over a client system being managed by Ansible, and the ability to send facts back to the Ansible server, could use this flaw to execute arbitrary code on the Ansible server using the Ansible server privileges.

## References
- https://access.redhat.com/errata/RHSA-2017:1244
- https://access.redhat.com/errata/RHSA-2017:1334
- https://access.redhat.com/errata/RHSA-2017:1476
- https://access.redhat.com/errata/RHSA-2017:1499
- https://access.redhat.com/errata/RHSA-2017:1599
- https://access.redhat.com/errata/RHSA-2017:1685
- http://www.securityfocus.com/bid/97595
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-7466
