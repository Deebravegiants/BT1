# [M] StarRocks Query Detail Endpoint Returns Every User's Query History

## Summary
Severity: Medium
Advisory: CVE-2026-82306
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82306
Type: osv

## Details
StarRocks through 4.0.13 contains an information disclosure vulnerability in the query_detail endpoint that returns unfiltered query history for all users. Authenticated attackers with low privileges can access full SQL text, execution plans, and profiling data from every query executed by other users, including statements containing credentials.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82306.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82306
- https://www.vulncheck.com/advisories/starrocks-query-detail-endpoint-returns-every-user-s-query-history
- https://github.com/StarRocks/starrocks/issues/75747
- https://github.com/StarRocks/starrocks
- https://github.com/StarRocks/starrocks/blob/4.0.13/fe/fe-core/src/main/java/com/starrocks/http/rest/QueryDetailAction.java
