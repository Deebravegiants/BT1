# [H] Infinite Loop in Apache Sanselan

## Summary
Severity: High
Advisory: GHSA-g99m-3m46-4gm9
CVE: CVE-2018-17202
CWE: CWE-835
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-05-14
Source: https://github.com/advisories/GHSA-g99m-3m46-4gm9
Type: github-advisory

## Affected
- Maven: `org.apache.sanselan:sanselan` — affected >=0

## Details
Certain input files could make the code to enter into an infinite loop when Apache Sanselan 0.97-incubator was used to parse them, which could be used in a DoS attack. Note that Apache Sanselan (incubating) was renamed to Apache Commons Imaging.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-17202
- https://lists.apache.org/thread.html/69204376d12205b0d2d90e6fcbeebb99b894e6db88c8ff565c4e1efa@%3Cdev.commons.apache.org%3E
