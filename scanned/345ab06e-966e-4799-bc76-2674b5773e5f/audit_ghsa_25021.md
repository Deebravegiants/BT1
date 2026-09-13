# [M] Insecure transport protocol in Gradle

## Summary
Severity: Medium
Advisory: GHSA-pprq-4488-wgqx
CVE: CVE-2019-11065
CWE: CWE-319
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-pprq-4488-wgqx
Type: github-advisory

## Affected
- Maven: `org.gradle:gradle-core` — affected >=1.4 <5.4.0

## Details
Gradle versions from 1.4 to 5.3.1 use an insecure HTTP URL to download dependencies when the built-in JavaScript or CoffeeScript Gradle plugins are used. Dependency artifacts could have been maliciously compromised by a MITM attack against the ajax.googleapis.com web site.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11065
- https://github.com/gradle/gradle/pull/8927
- https://github.com/gradle/gradle
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WVXOXNLAYRGPKAZV63PYNV3HF27JW2MW
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/Y43P7SVDJOG6OUDVFR4ZIDITZLNHPGTO
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/YQ5CGOV5QVQCSPGE3WRZDKUGIXLHSZDR
