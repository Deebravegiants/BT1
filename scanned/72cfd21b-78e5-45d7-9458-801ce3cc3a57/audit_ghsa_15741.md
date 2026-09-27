# [H] Apache Syncope Improper Input Validation vulnerability

## Summary
Severity: High
Advisory: GHSA-8pxv-x6jq-5vw9
CVE: CVE-2024-38503
CWE: CWE-20, CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-07-22
Source: https://github.com/advisories/GHSA-8pxv-x6jq-5vw9
Type: github-advisory

## Affected
- Maven: `org.apache.syncope.client.idrepo:syncope-client-idrepo-common-ui` — affected >=2.1.0 <3.0.8
- Maven: `org.apache.syncope.client.idrepo:syncope-client-idrepo-console` — affected >=2.1.0 <3.0.8

## Details
When editing a user, group or any object in the Syncope Console, HTML tags could be added to any text field and could lead to potential exploits.
The same vulnerability was found in the Syncope Enduser, when editing "Personal Information" or "User Requests".

Users are recommended to upgrade to version 3.0.8, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-38503
- https://github.com/apache/syncope/commit/12e65f5fb12ad87ce0b223b3c2bb39025a4521e4
- https://github.com/apache/syncope
- https://github.com/apache/syncope/releases/tag/syncope-3.0.8
- https://syncope.apache.org/security#cve-2024-38503-html-tags-can-be-injected-into-console-or-enduser
- https://www.openwall.com/lists/oss-security/2024/07/22/3
