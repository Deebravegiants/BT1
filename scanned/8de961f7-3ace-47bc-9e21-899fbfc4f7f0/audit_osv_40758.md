# [C] DHIS2 SQL injection in SQL View filter values

## Summary
Severity: Critical
Advisory: CVE-2026-55082
Aliases: GHSA-3288-cm98-664f
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-55082
Type: osv

## Details
DHIS2 is a flexible information system for data capture, management, validation, analytics and visualization. DHIS2 SQL View data endpoints allowed authenticated users with SQL View access to provide crafted filter values that were interpolated into generated SQL. An authenticated user with access to SQL View execution could manipulate SQL generated for SQL View filters and potentially access data outside the intended SQL View result set.

This is distinct from CVE-2026-55084, which tracks the related SQL View filter column-name injection.

Known affected release lines for this advisory: DHIS2 2.37, 2.38, and 2.39 before the 2026-06-09 EOS security updates.
Patched by the 2026-06-09 EOS security updates for 2.37, 2.38, and 2.39. The same value-slot hardening was already present on later supported branches through DHIS2-20174 / PR #22253.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55082.json
- https://github.com/dhis2/dhis2-core/security/advisories/GHSA-3288-cm98-664f
- https://nvd.nist.gov/vuln/detail/CVE-2026-55082
- https://github.com/dhis2/dhis2-core/pull/22253
- https://github.com/dhis2/dhis2-core/pull/24172
- https://github.com/dhis2/dhis2-core/pull/24173
- https://github.com/dhis2/dhis2-core/pull/24174
