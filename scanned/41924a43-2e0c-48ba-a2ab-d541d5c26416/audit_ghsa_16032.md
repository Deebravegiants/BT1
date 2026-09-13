# [M] Searching Opencast may cause a denial of service

## Summary
Severity: Medium
Advisory: GHSA-jh6x-7xfg-9cq2
CVE: CVE-2024-52797
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-11-20
Source: https://github.com/advisories/GHSA-jh6x-7xfg-9cq2
Type: github-advisory

## Affected
- Maven: `org.opencastproject:opencast-elasticsearch-impl` — affected >=11.4 <13.10
- Maven: `org.opencastproject:opencast-elasticsearch-impl` — affected >=14.0 <14.3
- Maven: `org.opencastproject:opencast-elasticsearch-impl` — affected >=15.0 <16.7

## Details
### Impact
First noticed in Opencast 13 and 14, Opencast's Elasticsearch integration may generate syntactically invalid Elasticsearch queries in relation to previously acceptable search queries.  From Opencast version 11.4 and newer, Elasticsearch queries are retried a configurable number of times in the case of error to handle temporary losses of connection to Elasticsearch.  These invalid queries would fail, causing the retry mechanism to begin requerying with the same syntactically invalid query immediately, in an infinite loop.  This causes a massive increase in log size which can in some cases cause a denial of service due to disk exhaustion.

### Patches
Opencast 13.10 and Opencast 14.3 contain patches (https://github.com/opencast/opencast/pull/5150, and https://github.com/opencast/opencast/pull/5033) which address the base issue, with Opencast 16.7 containing changes which harmonize the search behaviour between the admin UI and external API.  Users are strongly recommended to upgrade as soon as possible if running versions prior to 13.10 or 14.3.  While the relevant endpoints require (by default) `ROLE_ADMIN` or `ROLE_API_SERIES_VIEW`, the problem queries are otherwise innocuous.  This issue could be easily triggered by normal administrative work on an affected Opencast system.  If you are running a version newer than 13.10 and 14.3 *and* seeing different results when searching in your admin UI vs your external API or LMS, upgrading to 16.7 should resolve the issue.

### Workarounds
None identified.

### References
Pull Requests
- Preventing the infinite loop issue: https://github.com/opencast/opencast/pull/5150
- Sanitizing user input: https://github.com/opencast/opencast/pull/5033

### If you have any questions or comments about this advisory:
Open an issue in [our issue tracker](https://github.com/opencast/opencast/issues)
Email us at [security@opencast.org](mailto:security@opencast.org)

### Credit
Credit to Adilagha Aliyev of Graz University of Technology, Educational Technologies, adilagha.aliyev@gmail.com

## References
- https://github.com/opencast/opencast/security/advisories/GHSA-jh6x-7xfg-9cq2
- https://nvd.nist.gov/vuln/detail/CVE-2024-52797
- https://github.com/opencast/opencast/pull/5033
- https://github.com/opencast/opencast/pull/5150
- https://github.com/opencast/opencast/commit/3d5ebd163674eb18e070f52b64a18f92188f98c3
- https://github.com/opencast/opencast
- https://github.com/opencast/opencast/blob/7ad05f72814f057130122904015d471cfe5f4c58/docs/guides/admin/docs/changelog/older-versions/opencast-16.md?plain=1#L74
