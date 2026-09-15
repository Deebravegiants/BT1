# [H] CVE-2018-16881

## Summary
Severity: High
Advisory: CVE-2018-16881
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-25
Source: https://osv.dev/vulnerability/CVE-2018-16881
Type: osv

## Details
A denial of service vulnerability was found in rsyslog in the imptcp module. An attacker could send a specially crafted message to the imptcp socket, which would cause rsyslog to crash. Versions before 8.27.0 are vulnerable.

## References
- https://access.redhat.com/errata/RHBA-2019:2501
- https://access.redhat.com/errata/RHSA-2019:2110
- https://access.redhat.com/errata/RHSA-2019:2437
- https://access.redhat.com/errata/RHSA-2019:2439
- https://lists.debian.org/debian-lts-announce/2022/05/msg00028.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16881
