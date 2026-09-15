# [H] Dependency verification bypass in Gradle

## Summary
Severity: High
Advisory: BIT-gradle-2022-23630
Aliases: CVE-2022-23630, GHSA-9pf5-88jw-3qgr
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gradle-2022-23630
Type: osv

## Affected
- Bitnami: `gradle` — affected >=6.2.0 <7.3.4

## Details
Gradle is a build tool with a focus on build automation and support for multi-language development. In some cases, Gradle may skip that verification and accept a dependency that would otherwise fail the build as an untrusted external artifact. This occurs when dependency verification is disabled on one or more configurations and those configurations have common dependencies with other configurations that have dependency verification enabled. If the configuration that has dependency verification disabled is resolved first, Gradle does not verify the common dependencies for the configuration that has dependency verification enabled. Gradle 7.4 fixes that issue by validating artifacts at least once if they are present in a resolved configuration that has dependency verification active. For users who cannot update either do not use `ResolutionStrategy.disableDependencyVerification()` and do not use plugins that use that method to disable dependency verification for a single configuration or make sure resolution of configuration that disable that feature do not happen in builds that resolve configuration where the feature is enabled.

## References
- https://docs.gradle.org/7.4/release-notes.html
- https://github.com/gradle/gradle/commit/88ab9b652933bc3b2e3161b31ad8b8f4f0516351
- https://github.com/gradle/gradle/security/advisories/GHSA-9pf5-88jw-3qgr
- https://nvd.nist.gov/vuln/detail/CVE-2022-23630
