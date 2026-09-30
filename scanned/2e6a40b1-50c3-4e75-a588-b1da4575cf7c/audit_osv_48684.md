# [M] CVE-2018-1114

## Summary
Severity: Medium
Advisory: CVE-2018-1114
Aliases: GHSA-gjjx-gqm4-wcgm
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-09-11
Source: https://osv.dev/vulnerability/CVE-2018-1114
Type: osv

## Details
It was found that URLResource.getLastModified() in Undertow closes the file descriptors only when they are finalized which can cause file descriptors to exhaust. This leads to a file handler leak.

## References
- https://access.redhat.com/errata/RHSA-2018:2643
- https://access.redhat.com/errata/RHSA-2018:2669
- https://access.redhat.com/errata/RHSA-2019:0877
- https://bugs.openjdk.java.net/browse/JDK-6956385
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-1114
- https://issues.jboss.org/browse/UNDERTOW-1338
