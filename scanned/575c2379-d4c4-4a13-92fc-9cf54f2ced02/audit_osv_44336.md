# [M] Baserow before 2.3.1 Unauthenticated Data Disclosure via Discarded Permission Check on Builder Data Sources

## Summary
Severity: Medium
Advisory: CVE-2026-81335
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81335
Type: osv

## Details
Baserow dispatches an Application Builder data source without acting on the result of its permission check. The dispatch and record-name views in backend/src/baserow/contrib/builder/api/data_sources/views.py are declared with a permission class that admits any caller, so a request carrying no credential reaches the handler. DataSourceService.dispatch_data_sources in backend/src/baserow/contrib/builder/data_sources/service.py then calls check_multiple_permissions without asking it to raise, and neither stores nor examines the mapping of denials it returns, so a denied check leaves execution to continue and the data source is dispatched whatever the caller's identity. The dispatch runs with the integration's own credentials, so an unauthenticated request naming a data source receives the rows and fields that source reads. Identifiers are small integers and can be enumerated. Version 2.3.1 passes raise_exception to the same call.

## References
- https://baserow.io
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81335.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-81335
- https://www.vulncheck.com/advisories/baserow-before-2.3.1-unauthenticated-data-disclosure-via-discarded-permission-check-on-builder-data-sources
- https://github.com/bram2w/baserow/blob/2.3.1/backend/src/baserow/contrib/builder/data_sources/service.py
- https://github.com/bram2w/baserow
- https://github.com/bram2w/baserow/blob/2.3.0/backend/src/baserow/contrib/builder/data_sources/service.py
