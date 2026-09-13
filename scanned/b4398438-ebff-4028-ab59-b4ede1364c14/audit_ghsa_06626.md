# [M] Apache Camel-JIRA: A set of non-Camel-prefixed Exchange header constants bypass the HTTP header filter

## Summary
Severity: Medium
Advisory: GHSA-64gv-6cq2-45jr
CVE: CVE-2026-48206
CWE: CWE-20, CWE-639
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-64gv-6cq2-45jr
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-jira` — affected >=4.0.0 <4.14.8
- Maven: `org.apache.camel:camel-jira` — affected >=4.15.0 <4.18.3
- Maven: `org.apache.camel:camel-jira` — affected >=4.19.0 <4.21.0

## Details
Improper Input Validation, Authorization Bypass Through User-Controlled Key vulnerability in Apache Camel JIRA component.

The camel-jira producers read their operation parameters - the issue key, project key, transition id, summary, type, assignee, components, watchers, link type, work-log minutes and others - from Exchange message headers. The header constants defined in JiraConstants (for example ISSUE_KEY = IssueKey, ISSUE_PROJECT_KEY = ProjectKey, ISSUE_TRANSITION_ID = IssueTransitionId, LINK_TYPE = linkType) used plain, non-Camel-prefixed values. Because these names do not start with the Camel / camel prefix, HttpHeaderFilterStrategy - which blocks only the Camel header namespace on the HTTP boundary - let them pass from an inbound HTTP request straight into the Exchange. In a route that bridges an HTTP consumer (for example platform-http) into a jira: producer, any HTTP client could therefore supply these headers and override the values the route intended, driving JIRA operations against the configured JIRA instance with the endpoint's configured service-account credentials - for example deleting or transitioning an arbitrary issue (via IssueKey / IssueTransitionId), creating an issue in a different project (via ProjectKey), modifying issue fields, adding or removing watchers, or logging work. The operations are bounded by what the configured service account is permitted to do. No credentials are required from the attacker when the bridging consumer is unauthenticated.
This issue affects Apache Camel: from 4.0.0 before 4.14.8, from 4.15.0 before 4.18.3, from 4.19.0 before 4.21.0.

Users are recommended to upgrade to version 4.21.0, which fixes the issue. If users are on the 4.14.x LTS releases stream, then they are suggested to upgrade to 4.14.8. If users are on the 4.18.x releases stream, then they are suggested to upgrade to 4.18.3. After upgrading, routes that drive JIRA operations via the raw header names must use the CamelJira* names (for example CamelJiraIssueKey) instead of the old values. For deployments that cannot upgrade immediately, strip the camel-jira control headers from any untrusted ingress before the jira: producer (for example removing the IssueKey, ProjectKey, IssueTransitionId and related headers at the start of the route), and set the required JIRA operation parameters from a trusted source.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-48206
- https://github.com/apache/camel/pull/23417
- https://github.com/apache/camel/pull/23460
- https://github.com/apache/camel/pull/23472
- https://github.com/apache/camel/commit/024704f95f16d1260304054088fa0b34acb57ebf
- https://github.com/apache/camel/commit/3240a174a3707ba2b1d893c4ac0880829e0c9233
- https://github.com/apache/camel/commit/6863ea624605ab3fa8827c43a4c5df333f767dc4
- https://camel.apache.org/security/CVE-2026-48206.html
- https://github.com/apache/camel
- https://github.com/apache/camel/releases/tag/camel-4.14.8
- https://github.com/apache/camel/releases/tag/camel-4.18.3
- https://github.com/apache/camel/releases/tag/camel-4.21.0
- https://issues.apache.org/jira/browse/CAMEL-23576
- http://www.openwall.com/lists/oss-security/2026/07/05/20
