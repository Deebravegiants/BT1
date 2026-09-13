# [H] CVE-2021-31828

## Summary
Severity: High
Advisory: CVE-2021-31828
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N)
Published: 2021-05-06
Source: https://osv.dev/vulnerability/CVE-2021-31828
Type: osv

## Details
An SSRF issue in Open Distro for Elasticsearch (ODFE) before 1.13.1.0 allows an existing privileged user to enumerate listening services or interact with configured resources via HTTP requests exceeding the Alerting plugin's intended scope.

## References
- https://opendistro.github.io/for-elasticsearch-docs/version-history/
- https://rotem-bar.com/ssrf-in-open-distro-for-elasticsearch-cve-2021-31828
- https://github.com/opendistro-for-elasticsearch/alerting/pull/353
