# [M] Denial of service vulnerability on creating a Launch with too many recursively nested elements in reportportal

## Summary
Severity: Medium
Advisory: GHSA-mj24-gpw7-23m9
CVE: CVE-2023-25822
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-10-10
Source: https://github.com/advisories/GHSA-mj24-gpw7-23m9
Type: github-advisory

## Affected
- Maven: `com.epam.reportportal:service-api` — affected >=0 <5.10.0

## Details
### Impact
ReportPortal database becomes unstable and reporting almost fully stops except for small launches with approximately 1 test inside when the test_item.path field is exceeded the allowable "ltree" field type indexing limit (path length>=120 approximately, recursive nesting of the nested steps). 

REINDEX INDEX path_gist_idx and path_idx aren't helped. 

### Patches
The problem was fixed in `service-api` module of version `5.10.0` (product release [23.2](https://reportportal.io/docs/releases/Version23.2/)), where the maximum number of nested elements were programmatically limited.

### Workarounds
After deletion of the data with long paths, and reindexing both indexes (path_gist_idx and path_idx), the database becomes stable and ReportPortal is working properly.

## References
- https://github.com/reportportal/reportportal/security/advisories/GHSA-mj24-gpw7-23m9
- https://nvd.nist.gov/vuln/detail/CVE-2023-25822
- https://github.com/reportportal/reportportal
- https://github.com/reportportal/reportportal/releases/tag/v23.2
- https://reportportal.io/docs/releases/Version23.2
