# [M] Improper Restriction of Rendered UI Layers or Frames in Apache nifif

## Summary
Severity: Medium
Advisory: GHSA-2xpp-75vr-22vq
CVE: CVE-2018-17192
CWE: CWE-1021
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-12-20
Source: https://github.com/advisories/GHSA-2xpp-75vr-22vq
Type: github-advisory

## Affected
- Maven: `org.apache.nifi:nifi` — affected >=1.0.0 <1.8.0

## Details
The X-Frame-Options headers were applied inconsistently on some HTTP responses, resulting in duplicate or missing security headers. Some browsers would interpret these results incorrectly, allowing clickjacking attacks. Mitigation: The fix to consistently apply the security headers was applied on the Apache NiFi 1.8.0 release. Users running a prior 1.x release should upgrade to the appropriate release.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-17192
- https://github.com/apache/nifi/commit/dbf259508c2b8e176d8cb837177aaadbf44f0670
- https://github.com/advisories/GHSA-2xpp-75vr-22vq
- https://issues.apache.org/jira/browse/NIFI-5258
- https://nifi.apache.org/security.html#CVE-2018-17192
