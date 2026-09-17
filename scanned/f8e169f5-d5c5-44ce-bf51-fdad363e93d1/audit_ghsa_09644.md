# [M] CKAN has Unauthenticated Authorization Bypass in `datastore_search_sql`

## Summary
Severity: Medium
Advisory: GHSA-cg4x-64p3-x59h
CVE: CVE-2026-42032
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-04-30
Source: https://github.com/advisories/GHSA-cg4x-64p3-x59h
Type: github-advisory

## Affected
- PyPI: `ckan` — affected >=0 <2.10.10
- PyPI: `ckan` — affected >=2.11.0 <2.11.5

## Details
### Impact

A vulnerability in `datastore_search_sql` allowed attackers to bypass authorization in order to gain access to private resources and PostgreSQL system information

### Patches
The issue has been patched in CKAN 2.10.10 and CKAN 2.11.5

### Workarounds
Disable the DataStore SQL search (`ckan.datastore.sqlsearch.enabled = false`). Note that the SQL search is disabled by default.

### More information

As stated in the [documentation](https://docs.ckan.org/en/2.11/maintaining/configuration.html#ckan-datastore-sqlsearch-enabled), this action function has protections that offer some safety but are not designed to prevent all types of abuse. Depending on the sensitivity of private data in your DataStore and the likelihood of abuse of your site, you may choose to disable this action function or restrict its use with a [`IAuthFunctions`](https://docs.ckan.org/en/2.11/extensions/plugin-interfaces.html#ckan.plugins.interfaces.IAuthFunctions) plugin.

### Credits

* Reported by Arvin Shivram of Brutecat Security

## References
- https://github.com/ckan/ckan/security/advisories/GHSA-cg4x-64p3-x59h
- https://nvd.nist.gov/vuln/detail/CVE-2026-42032
- https://docs.ckan.org/en/2.10/changelog.html#v-2-10-10-2026-04-29
- https://docs.ckan.org/en/2.11/changelog.html#v-2-11-5-2026-04-29
- https://docs.ckan.org/en/2.11/extensions/plugin-interfaces.html#ckan.plugins.interfaces.IAuthFunctions
- https://docs.ckan.org/en/2.11/maintaining/configuration.html#ckan-datastore-sqlsearch-enabled
- https://github.com/ckan/ckan
