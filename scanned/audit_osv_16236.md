# [M] CVE-2019-3805

## Summary
Severity: Medium
Advisory: CVE-2019-3805
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-05-03
Source: https://osv.dev/vulnerability/CVE-2019-3805
Type: osv

## Details
A flaw was discovered in wildfly versions up to 16.0.0.Final that would allow local users who are able to execute init.d script to terminate arbitrary processes on the system. An attacker could exploit this by modifying the PID file in /var/run/jboss-eap/ allowing the init.d script to terminate any process as root.

## References
- https://access.redhat.com/errata/RHSA-2019:1106
- https://access.redhat.com/errata/RHSA-2019:1107
- https://access.redhat.com/errata/RHSA-2019:1108
- https://access.redhat.com/errata/RHSA-2019:1140
- https://access.redhat.com/errata/RHSA-2019:2413
- https://access.redhat.com/errata/RHSA-2020:0727
- https://security.netapp.com/advisory/ntap-20190517-0004/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3805
