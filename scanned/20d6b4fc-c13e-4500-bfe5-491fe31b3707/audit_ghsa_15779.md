# [M] Apache NiFi vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-h658-qqv9-qwv8
CVE: CVE-2024-37389
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-07-08
Source: https://github.com/advisories/GHSA-h658-qqv9-qwv8
Type: github-advisory

## Affected
- Maven: `org.apache.nifi:nifi-web-ui` — affected >=1.10.0 <1.27.0
- Maven: `org.apache.nifi:nifi-web-ui` — affected >=2.0.0-M1 <2.0.0-M4

## Details
Apache NiFi 1.10.0 through 1.26.0 and 2.0.0-M1 through 2.0.0-M3 support a description field in the Parameter Context configuration that is vulnerable to cross-site scripting. An authenticated user, authorized to configure a Parameter Context, can enter arbitrary JavaScript code, which the client browser will execute within the session context of the authenticated user. Upgrading to Apache NiFi 1.27.0 or 2.0.0-M4 is the recommended mitigation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-37389
- https://github.com/apache/nifi/pull/8938
- https://github.com/apache/nifi/commit/1ea0bc1f7fa90ecff0ceb8b0c91a9aebeb05893b
- https://github.com/apache/nifi
- https://issues.apache.org/jira/browse/NIFI-13374
- https://lists.apache.org/thread/yso9fr0wtff53nk046h1o83hdyb1lrxh
