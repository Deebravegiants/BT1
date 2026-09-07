# [M] JetBrains Ktor information disclosure

## Summary
Severity: Medium
Advisory: GHSA-8qv4-773j-c979
CVE: CVE-2024-49580
CWE: CWE-524
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-10-17
Source: https://github.com/advisories/GHSA-8qv4-773j-c979
Type: github-advisory

## Affected
- Maven: `io.ktor:ktor-client-core-jvm` — affected >=0 <2.3.13

## Details
Improper caching in JetBrains Ktor before 3.0.0 in the `HttpCache` Plugin could lead to response information disclosure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-49580
- https://github.com/ktorio/ktor/pull/4337
- https://github.com/ktorio/ktor/pull/4368
- https://github.com/ktorio/ktor/commit/0665736fc35c8ab5525241e975f36819b67f9d3e
- https://github.com/ktorio/ktor/commit/d6c3a51df169c163e8f0b9ce77bbe543c70116ac
- https://github.com/ktorio/ktor
- https://github.com/ktorio/ktor/releases/tag/2.3.13
- https://www.jetbrains.com/privacy-security/issues-fixed
- https://youtrack.jetbrains.com/issue/KTOR-7483
