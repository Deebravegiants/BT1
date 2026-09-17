# [M] Improper Limitation of a Pathname to a Restricted Directory in WildFly

## Summary
Severity: Medium
Advisory: GHSA-w8r2-5j8x-x8j6
CVE: CVE-2018-10862
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-w8r2-5j8x-x8j6
Type: github-advisory

## Affected
- Maven: `org.wildfly.core:wildfly-server` — affected >=0 <6.0.0.Alpha3

## Details
WildFly Core before version 6.0.0.Alpha3 does not properly validate file paths in .war archives, allowing for the extraction of crafted .war archives to overwrite arbitrary files. This is an instance of the 'Zip Slip' vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-10862
- https://access.redhat.com/errata/RHSA-2018:2276
- https://access.redhat.com/errata/RHSA-2018:2277
- https://access.redhat.com/errata/RHSA-2018:2279
- https://access.redhat.com/errata/RHSA-2018:2423
- https://access.redhat.com/errata/RHSA-2018:2424
- https://access.redhat.com/errata/RHSA-2018:2425
- https://access.redhat.com/errata/RHSA-2018:2428
- https://access.redhat.com/errata/RHSA-2018:2643
- https://access.redhat.com/errata/RHSA-2019:0877
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10862
- https://snyk.io/research/zip-slip-vulnerability
