# [H] Apache NiFi Improper Input Validation vulnerability

## Summary
Severity: High
Advisory: GHSA-43fp-vwwg-qgv6
CVE: CVE-2018-17194
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-12-20
Source: https://github.com/advisories/GHSA-43fp-vwwg-qgv6
Type: github-advisory

## Affected
- Maven: `org.apache.nifi:nifi-framework-cluster` — affected >=1.0.0 <1.8.0

## Details
When a client request to a cluster node was replicated to other nodes in the cluster for verification, the Content-Length was forwarded. On a DELETE request, the body was ignored, but if the initial request had a Content-Length value other than 0, the receiving nodes would wait for the body and eventually timeout. Mitigation: The fix to check DELETE requests and overwrite non-zero Content-Length header values was applied on the Apache NiFi 1.8.0 release. Users running a prior 1.x release should upgrade to the appropriate release.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-17194
- https://github.com/apache/nifi/commit/1baead6f525046a613fc4fe494a0d193776ea70f
- https://github.com/apache/nifi/commit/748cf745628dab20b7e71f12b5dcfe6ed0bbf134
- https://github.com/apache/nifi
- https://issues.apache.org/jira/browse/NIFI-5628
- https://nifi.apache.org/security.html#CVE-2018-17194
