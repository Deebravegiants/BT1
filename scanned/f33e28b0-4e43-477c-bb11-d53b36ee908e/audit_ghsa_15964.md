# [M] Apache NiFi Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7mqj-xgf8-p59v
CVE: CVE-2024-45477
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-10-29
Source: https://github.com/advisories/GHSA-7mqj-xgf8-p59v
Type: github-advisory

## Affected
- Maven: `org.apache.nifi:nifi-web-ui` — affected >=1.10.0 <1.28.0
- Maven: `org.apache.nifi:nifi-web-ui` — affected >=2.0.0-M1 <2.0.0-M4

## Details
Apache NiFi 1.10.0 through 1.27.0 and 2.0.0-M1 through 2.0.0-M3 support a description field for Parameters in a Parameter Context configuration that is vulnerable to cross-site scripting. An authenticated user, authorized to configure a Parameter Context, can enter arbitrary JavaScript code, which the client browser will execute within the session context of the authenticated user. Upgrading to Apache NiFi 1.28.0 or 2.0.0-M4 is the recommended mitigation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45477
- https://github.com/apache/nifi/pull/9195
- https://github.com/apache/nifi/commit/153c87a7daaeebea9b119066285b840ea4056e09
- https://github.com/apache/nifi
- https://github.com/apache/nifi/blob/rel/nifi-1.27.0/nifi-nar-bundles/nifi-framework-bundle/nifi-framework/nifi-web/nifi-web-ui/src/main/webapp/js/nf/canvas/nf-parameter-contexts.js#L2197
- https://issues.apache.org/jira/browse/NIFI-13675
- https://lists.apache.org/thread/shdv0tw9hggj7tx9pl7g93mgok2lwbj9
- https://nifi.apache.org/documentation/security/#CVE-2024-45477
