# [H] CVE-2018-3831

## Summary
Severity: High
Advisory: CVE-2018-3831
Aliases: GHSA-r9fv-qpm9-rj4g
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-19
Source: https://osv.dev/vulnerability/CVE-2018-3831
Type: osv

## Details
Elasticsearch Alerting and Monitoring in versions before 6.4.1 or 5.6.12 have an information disclosure issue when secrets are configured via the API. The Elasticsearch _cluster/settings API, when queried, could leak sensitive configuration information such as passwords, tokens, or usernames. This could allow an authenticated Elasticsearch user to improperly view these details.

## References
- https://discuss.elastic.co/t/elastic-stack-6-4-1-and-5-6-12-security-update/149035
- https://www.elastic.co/community/security
