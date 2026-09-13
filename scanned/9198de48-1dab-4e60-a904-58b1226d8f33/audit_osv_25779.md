# [M] Discourse-Jira could make SSRF attack by setting Jira URL to an arbitrary location

## Summary
Severity: Medium
Advisory: CVE-2023-44384
Aliases: GHSA-pmv5-h2x6-35fh
CVSS: 4.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:N/A:N)
Published: 2023-10-06
Source: https://osv.dev/vulnerability/CVE-2023-44384
Type: osv

## Details
Discourse-jira is a Discourse plugin allows Jira projects, issue types, fields and field options will be synced automatically. An administrator user can make an SSRF attack by setting the Jira URL to an arbitrary location and enabling the `discourse_jira_verbose_log` site setting. A moderator user could manipulate the request path to the Jira API, allowing them to perform arbitrary GET requests using the Jira API credentials, potentially with elevated permissions, used by the application.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/44xxx/CVE-2023-44384.json
- https://github.com/discourse/discourse-jira/security/advisories/GHSA-pmv5-h2x6-35fh
- https://nvd.nist.gov/vuln/detail/CVE-2023-44384
- https://github.com/discourse/discourse-jira/commit/8a2d3ad228883199fd5f081cc93d173c88e2e48f
- https://github.com/discourse/discourse-jira/pull/50
