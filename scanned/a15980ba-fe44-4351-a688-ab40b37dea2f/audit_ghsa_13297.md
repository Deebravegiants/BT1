# [C] postgraas-server vulnerable to SQL injection

## Summary
Severity: Critical
Advisory: GHSA-vghm-8cjp-hjw6
CVE: CVE-2018-25088
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-18
Source: https://github.com/advisories/GHSA-vghm-8cjp-hjw6
Type: github-advisory

## Affected
- PyPI: `postgraas-server` — affected >=0 <2.0.0

## Details
A vulnerability, which was classified as critical, was found in Blue Yonder postgraas_server up to 2.0.0b2. Affected is the function `_create_pg_connection/create_postgres_db` of the file `postgraas_server/backends/postgres_cluster/postgres_cluster_driver.py` of the component PostgreSQL Backend Handler. The manipulation leads to sql injection. Upgrading to version 2.0.0 is able to address this issue. The patch is identified as 7cd8d016edc74a78af0d81c948bfafbcc93c937c. It is recommended to upgrade the affected component. VDB-234246 is the identifier assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-25088
- https://github.com/blue-yonder/postgraas_server/commit/7cd8d016edc74a78af0d81c948bfafbcc93c937c
- https://github.com/blue-yonder/postgraas_server
- https://github.com/blue-yonder/postgraas_server/releases/tag/v2.0.0
- https://vuldb.com/?ctiid.234246
- https://vuldb.com/?id.234246
