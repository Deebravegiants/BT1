# [H] BIT-gradle-2021-41584

## Summary
Severity: High
Advisory: BIT-gradle-2021-41584
Aliases: CVE-2021-41584
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gradle-2021-41584
Type: osv

## Affected
- Bitnami: `gradle` — affected >=2020.4.0 <2021.1.3

## Details
Gradle Enterprise before 2021.1.3 can allow unauthorized viewing of a response (information disclosure of possibly sensitive build/configuration details) via a crafted HTTP request with the X-Gradle-Enterprise-Ajax-Request header.

## References
- https://security.gradle.com/advisory/2021-02
- https://nvd.nist.gov/vuln/detail/CVE-2021-41584
