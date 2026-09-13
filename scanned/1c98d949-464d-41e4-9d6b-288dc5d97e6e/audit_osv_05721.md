# [M] Gradle has incorrect permission assignment for symlinked files used in copy or archiving operations

## Summary
Severity: Medium
Advisory: BIT-gradle-2023-44387
Aliases: CVE-2023-44387, GHSA-43r3-pqhv-f7h9
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gradle-2023-44387
Type: osv

## Affected
- Bitnami: `gradle` — affected >=8.0.0 <8.4.0

## Details
Gradle is a build tool with a focus on build automation and support for multi-language development. When copying or archiving symlinked files, Gradle resolves them but applies the permissions of the symlink itself instead of the permissions of the linked file to the resulting file. This leads to files having too much permissions given that symlinks usually are world readable and writeable. While it is unlikely this results in a direct vulnerability for the impacted build, it may open up attack vectors depending on where build artifacts end up being copied to or un-archived. In versions 7.6.3, 8.4 and above, Gradle will now properly use the permissions of the file pointed at by the symlink to set permissions of the copied or archived file.

## References
- https://github.com/gradle/gradle/commit/3b406191e24d69e7e42dc3f3b5cc50625aa930b7
- https://github.com/gradle/gradle/releases/tag/v7.6.3
- https://github.com/gradle/gradle/releases/tag/v8.4.0
- https://github.com/gradle/gradle/security/advisories/GHSA-43r3-pqhv-f7h9
- https://security.netapp.com/advisory/ntap-20231110-0006/
- https://nvd.nist.gov/vuln/detail/CVE-2023-44387
