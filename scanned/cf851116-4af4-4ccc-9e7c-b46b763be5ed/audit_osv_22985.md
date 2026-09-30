# [H] OpenSearch Notifications is vulnerable to Server-Side Request Forgery (SSRF)

## Summary
Severity: High
Advisory: CVE-2022-41906
Aliases: GHSA-pfc4-3436-jgrw
CVSS: 7.7 (CVSS:3.0/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:N)
Published: 2022-11-11
Source: https://osv.dev/vulnerability/CVE-2022-41906
Type: osv

## Details
OpenSearch Notifications is a notifications plugin for OpenSearch that enables other plugins to send notifications via Email, Slack, Amazon Chime, Custom web-hook etc channels. A potential SSRF issue in OpenSearch Notifications Plugin starting in 2.0.0 and prior to 2.2.1 could allow an existing privileged user to enumerate listening services or interact with configured resources via HTTP requests exceeding the Notification plugin's intended scope. OpenSearch 2.2.1+ contains the fix for this issue. There are currently no recommended workarounds.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41906.json
- https://github.com/opensearch-project/notifications/security/advisories/GHSA-pfc4-3436-jgrw
- https://nvd.nist.gov/vuln/detail/CVE-2022-41906
- https://github.com/opensearch-project/notifications/pull/496
- https://github.com/opensearch-project/notifications/pull/507
