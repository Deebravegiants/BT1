# [M] Apache StreamPipes has possibility of SSRF in pipeline element installation process

## Summary
Severity: Medium
Advisory: GHSA-9gr7-gh74-qg9x
CVE: CVE-2024-31979
CWE: CWE-918
Ecosystem: Maven, PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-07-17
Source: https://github.com/advisories/GHSA-9gr7-gh74-qg9x
Type: github-advisory

## Affected
- Maven: `org.apache.streampipes:streampipes-parent` — affected >=0 <0.95.0
- PyPI: `streampipes` — affected >=0 <0.95.0

## Details
Server-Side Request Forgery (SSRF) vulnerability in Apache StreamPipes during installation process of pipeline elements.
Previously, StreamPipes allowed users to configure custom endpoints from which to install additional pipeline elements. 
These endpoints were not properly validated, allowing an attacker to get StreamPipes to send an HTTP GET request to an arbitrary address.

This issue affects Apache StreamPipes: through 0.93.0.

Users are recommended to upgrade to version 0.95.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-31979
- https://github.com/apache/streampipes/commit/cd5a7b46e3383573f0f2b51da4b7306d4936aa3f
- https://github.com/apache/streampipes
- https://github.com/apache/streampipes/releases/tag/release%2F0.95.0
- https://github.com/pypa/advisory-database/tree/main/vulns/streampipes/PYSEC-2024-174.yaml
- https://lists.apache.org/thread/8lryp3bxnby9kmk13odkz2jbfdjfvf0y
- http://www.openwall.com/lists/oss-security/2024/07/16/11
