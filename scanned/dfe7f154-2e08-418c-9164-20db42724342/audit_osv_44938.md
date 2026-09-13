# [C] Renovate before 44.14.7 Command Injection via gradle-wrapper

## Summary
Severity: Critical
Advisory: CVE-2026-88886
Aliases: GHSA-7chm-46wx-888m
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88886
Type: osv

## Details
Renovate is a dependency update automation tool. In versions before 44.14.7 (and in Mend Renovate CE/EE distributions before 15.4.0, and the mend-renovate-enterprise-edition Helm chart before 10.4.0), the manager/gradle-wrapper module does not escape the distributionUrl value read from a repository's gradle/wrapper/gradle-wrapper.properties file before invoking the Gradle Wrapper CLI. In self-hosted deployments configured with binarySource=docker and allowedUnsafeExecutions=['gradleWrapper', ...], a repository that supplies a crafted distributionUrl (for example, appending a shell metacharacter and command) can cause arbitrary commands to be executed as the Renovate user when Renovate processes a Gradle Wrapper update. The issue is fixed in Renovate 44.14.7; as a workaround, remove 'gradleWrapper' from allowedUnsafeExecutions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88886.json
- https://github.com/renovatebot/renovate/security/advisories/GHSA-7chm-46wx-888m
- https://nvd.nist.gov/vuln/detail/CVE-2026-88886
- https://www.vulncheck.com/advisories/renovate-before-44.14.7-command-injection-via-gradle-wrapper
