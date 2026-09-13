# [M] Improper Privilege Management in X-Pack 

## Summary
Severity: Medium
Advisory: GHSA-m728-qvxh-xfjq
CVE: CVE-2017-8446
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-m728-qvxh-xfjq
Type: github-advisory

## Affected
- Maven: `org.elasticsearch.plugin:x-pack` — affected >=0 <5.5.2

## Details
The Reporting feature in X-Pack in versions prior to 5.5.2 and standalone Reporting plugin versions versions prior to 2.4.6 had an impersonation vulnerability. A user with the reporting_user role could execute a report with the permissions of another reporting user, possibly gaining access to sensitive data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-8446
- https://www.elastic.co/community/security
