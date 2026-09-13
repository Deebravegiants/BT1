# [H] BIT-gradle-2021-41588

## Summary
Severity: High
Advisory: BIT-gradle-2021-41588
Aliases: CVE-2021-41588
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gradle-2021-41588
Type: osv

## Affected
- Bitnami: `gradle` — affected >=2017.2.0 <2021.1.3

## Details
In Gradle Enterprise before 2021.1.3, a crafted request can trigger deserialization of arbitrary unsafe Java objects. The attacker must have the encryption and signing keys.

## References
- https://security.gradle.com/advisory/2021-03
- https://nvd.nist.gov/vuln/detail/CVE-2021-41588
