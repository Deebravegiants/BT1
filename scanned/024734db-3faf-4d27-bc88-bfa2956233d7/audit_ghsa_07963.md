# [H] Apache NiFi: Missing Authorization of Restricted Permissions for Component Updates

## Summary
Severity: High
Advisory: GHSA-c5w7-m8wf-xc77
CVE: CVE-2026-25903
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:A/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/S:P/AU:Y/R:I/V:C/RE:M/U:Amber (CVSS_V4)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-c5w7-m8wf-xc77
Type: github-advisory

## Affected
- Maven: `org.apache.nifi:nifi-web-api` — affected >=1.1.0 <2.8.0

## Details
Apache NiFi 1.1.0 through 2.7.2 are missing authorization when updating configuration properties on extension components that have specific Required Permissions based on the Restricted annotation. The Restricted annotation indicates additional privileges required to add the annotated component to the flow configuration, but framework authorization did not check restricted status when updating a component previously added. The missing authorization requires a more privileged user to add a restricted component to the flow configuration, but permits a less privileged user to make property configuration changes. Apache NiFi installations that do not implement different levels of authorization for Restricted components are not subject to this vulnerability because the framework enforces write permissions as the security boundary. Upgrading to Apache NiFi 2.8.0 is the recommended mitigation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-25903
- https://github.com/apache/nifi/commit/119f8881fbc3cbd0d522b0c549b841da3de01f64
- https://github.com/apache/nifi
- https://issues.apache.org/jira/browse/NIFI-15567
- https://lists.apache.org/thread/jf6bkt9sk6xvshy8xyxv3vtlxd340345
- http://www.openwall.com/lists/oss-security/2026/02/16/1
