# [M] Missing Encryption of Sensitive Data in arrow-kt Arrow

## Summary
Severity: Medium
Advisory: GHSA-rcj2-vvjx-87pm
CVE: CVE-2019-11404
CWE: CWE-311
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-04-22
Source: https://github.com/advisories/GHSA-rcj2-vvjx-87pm
Type: github-advisory

## Affected
- Maven: `io.arrow-kt:arrow-ank-gradle` — affected >=0 <0.9.0

## Details
arrow-kt Arrow before 0.9.0 resolved Gradle build artifacts (for compiling and building the published JARs) over HTTP instead of HTTPS. Any of these dependent artifacts could have been maliciously compromised by an MITM attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11404
- https://github.com/arrow-kt/ank/issues/35
- https://github.com/arrow-kt/arrow/issues/1310
- https://github.com/arrow-kt/ank/pull/36
- https://github.com/arrow-kt/arrow/commit/74198dab522393487d5344f194dc21208ab71ae8
- https://github.com/arrow-kt/arrow/releases/tag/0.9.0
