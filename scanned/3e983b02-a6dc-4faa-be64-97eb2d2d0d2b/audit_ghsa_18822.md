# [M] Jenkins Eggplant Runner Plugin protection mechanism disabled

## Summary
Severity: Medium
Advisory: GHSA-w5r3-gr8w-7fj5
CVE: CVE-2025-64135
CWE: CWE-1188
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-10-29
Source: https://github.com/advisories/GHSA-w5r3-gr8w-7fj5
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:eggplant-runner` — affected >=0

## Details
Jenkins Eggplant Runner Plugin 0.0.1.301.v963cffe8ddb_8 and earlier sets the Java system property `jdk.http.auth.tunneling.disabledSchemes` to an empty value as part of applying a proxy configuration.

This disables a protection mechanism of the Java runtime addressing CVE-2016-5597.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-64135
- https://github.com/jenkinsci/eggplant-runner-plugin
- https://www.jenkins.io/security/advisory/2025-10-29/#SECURITY-3326
- http://www.openwall.com/lists/oss-security/2025/10/29/2
