# [H] Apache Axis Improper Input Validation vulnerability

## Summary
Severity: High
Advisory: GHSA-hr2c-p8rh-238h
CVE: CVE-2023-51441
CWE: CWE-20, CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-01-06
Source: https://github.com/advisories/GHSA-hr2c-p8rh-238h
Type: github-advisory

## Affected
- Maven: `org.apache.axis:axis` — affected >=0
- Maven: `axis:axis` — affected >=0

## Details
** UNSUPPORTED WHEN ASSIGNED ** Improper Input Validation vulnerability in Apache Axis allowed users with access to the admin service to perform possible SSRF.
This issue affects Apache Axis through 1.3.

As Axis 1 has been EOL, we recommend you migrate to a different SOAP engine, such as Apache Axis 2/Java. Alternatively you could use a build of Axis with the patch from https://github.com/apache/axis-axis1-java/commit/685c309febc64aa393b2d64a05f90e7eb9f73e06 applied. The Apache Axis project does not expect to create an Axis 1.x release 
fixing this problem, though contributors that would like to work towards this are welcome.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-51441
- https://github.com/apache/axis-axis1-java/commit/685c309febc64aa393b2d64a05f90e7eb9f73e06
- https://github.com/apache/axis-axis1-java
- https://lists.apache.org/thread/8nrm5thop8f82pglx4o0jg8wmvy6d9yd
