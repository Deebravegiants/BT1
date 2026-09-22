# [C] Command injection in Alluxio

## Summary
Severity: Critical
Advisory: GHSA-j3ch-vjph-8q6v
CVE: CVE-2022-23848
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-21
Source: https://github.com/advisories/GHSA-j3ch-vjph-8q6v
Type: github-advisory

## Affected
- Maven: `org.alluxio:alluxio-core-common` — affected >=0 <2.7.3

## Details
In Alluxio before 2.7.3, the logserver does not validate the input stream. NOTE: this is not the same as the CVE-2021-44228 Log4j vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23848
- https://www.alluxio.io/download/releases/alluxio-2-7-3-release
