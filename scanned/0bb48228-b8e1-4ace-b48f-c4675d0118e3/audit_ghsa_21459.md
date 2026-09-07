# [H] FusionAuth vulnerable to directory traversal attack

## Summary
Severity: High
Advisory: GHSA-rmcx-fg5w-x8j9
CVE: CVE-2022-45921
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-11-28
Source: https://github.com/advisories/GHSA-rmcx-fg5w-x8j9
Type: github-advisory

## Affected
- Maven: `io.fusionauth:fusionauth-java-client` — affected >=1.37.0 <1.41.3

## Details
FusionAuth before 1.41.3 allows a file outside of the application root to be viewed or retrieved using an HTTP request. To be specific, an attacker may be able to view or retrieve any file readable by the user running the FusionAuth process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45921
- https://github.com/FusionAuth/fusionauth-issues/issues/1983
- https://fusionauth.io/docs/v1/tech/release-notes
- https://github.com/FusionAuth/fusionauth-java-client
