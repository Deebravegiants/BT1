# [M] Possible local file exfiltration by XML External entity injection

## Summary
Severity: Medium
Advisory: BIT-gradle-2023-42445
Aliases: CVE-2023-42445, GHSA-mrff-q8qj-xvg8
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gradle-2023-42445
Type: osv

## Affected
- Bitnami: `gradle` — affected >=8.0.0 <8.4.0

## Details
Gradle is a build tool with a focus on build automation and support for multi-language development. In some cases, when Gradle parses XML files, resolving XML external entities is not disabled. Combined with an Out Of Band XXE attack (OOB-XXE), just parsing XML can lead to exfiltration of local text files to a remote server. Gradle parses XML files for several purposes. Most of the time, Gradle parses XML files it generated or were already present locally. Only Ivy XML descriptors and Maven POM files can be fetched from remote repositories and parsed by Gradle. In Gradle 7.6.3 and 8.4, resolving XML external entities has been disabled for all use cases to protect against this vulnerability. Gradle will now refuse to parse XML files that have XML external entities.

## References
- https://github.com/gradle/gradle/releases/tag/v7.6.3
- https://github.com/gradle/gradle/releases/tag/v8.4.0
- https://github.com/gradle/gradle/security/advisories/GHSA-mrff-q8qj-xvg8
- https://security.netapp.com/advisory/ntap-20231110-0006/
- https://nvd.nist.gov/vuln/detail/CVE-2023-42445
