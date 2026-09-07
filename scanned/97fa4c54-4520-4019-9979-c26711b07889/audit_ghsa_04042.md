# [H] Improper Input Validation in Apache Sanselan

## Summary
Severity: High
Advisory: GHSA-rjx9-2936-9ffx
CVE: CVE-2018-17201
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-05-14
Source: https://github.com/advisories/GHSA-rjx9-2936-9ffx
Type: github-advisory

## Affected
- Maven: `org.apache.sanselan:sanselan` — affected >=0

## Details
Certain input files could make the code hang when Apache Sanselan 0.97-incubator was used to parse them, which could be used in a DoS attack. Note that Apache Sanselan (incubating) was renamed to Apache Commons Imaging.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-17201
- https://lists.apache.org/thread.html/cd37861963aa6d2694c8947d464c99614d3e1a9db6c1a2a8b7b5840a@%3Cdev.commons.apache.org%3E
