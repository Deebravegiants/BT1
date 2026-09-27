# [M] Dependency-Track vulnerable to logging of API keys in clear text when handling API requests using keys with insufficient permissions

## Summary
Severity: Medium
Advisory: CVE-2022-39351
Aliases: GHSA-gh7v-4hxp-gqp4
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-10-25
Source: https://osv.dev/vulnerability/CVE-2022-39351
Type: osv

## Details
Dependency-Track is a Component Analysis platform that allows organizations to identify and reduce risk in the software supply chain. Prior to version 4.6.0, performing an API request using a valid API key with insufficient permissions causes the API key to be written to Dependency-Track's audit log in clear text. Actors with access to the audit log can exploit this flaw to gain access to valid API keys. The issue has been fixed in Dependency-Track 4.6.0. Instead of logging the entire API key, only the last 4 characters of the key will be logged. It is strongly recommended to check historic logs for occurrences of this behavior, and re-generating API keys in case of leakage.

## References
- https://docs.dependencytrack.org/changelog/
- https://github.com/DependencyTrack/dependency-track/blob/4.5.0/src/main/docker/logback.xml
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39351.json
- https://github.com/DependencyTrack/dependency-track/security/advisories/GHSA-gh7v-4hxp-gqp4
- https://nvd.nist.gov/vuln/detail/CVE-2022-39351
