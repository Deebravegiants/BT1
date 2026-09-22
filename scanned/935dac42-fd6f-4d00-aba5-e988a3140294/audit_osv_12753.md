# [M] CVE-2018-14627

## Summary
Severity: Medium
Advisory: CVE-2018-14627
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-09-04
Source: https://osv.dev/vulnerability/CVE-2018-14627
Type: osv

## Details
The IIOP OpenJDK Subsystem in WildFly before version 14.0.0 does not honour configuration when SSL transport is required. Servers before this version that are configured with the following setting allow clients to create plaintext connections: <transport-config confidentiality="required" trust-in-target="supported"/>

## References
- https://access.redhat.com/errata/RHSA-2018:3527
- https://access.redhat.com/errata/RHSA-2018:3528
- https://access.redhat.com/errata/RHSA-2018:3529
- https://access.redhat.com/errata/RHSA-2018:3595
- https://issues.jboss.org/browse/WFLY-9107
- https://security.netapp.com/advisory/ntap-20181221-0002/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14627
