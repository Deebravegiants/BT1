# [H] Improper Authentication in Flask-AppBuilder

## Summary
Severity: High
Advisory: GHSA-m3rf-7m4w-r66q
CVE: CVE-2021-41265
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-12-09
Source: https://github.com/advisories/GHSA-m3rf-7m4w-r66q
Type: github-advisory

## Affected
- PyPI: `Flask-AppBuilder` — affected >=0 <3.3.4

## Details
### Impact
Improper authentication on the REST API. Allows for a malicious actor with a carefully crafted request to successfully authenticate and gain access to existing protected REST API endpoints. Only affects non database authentication types, and new REST API endpoints.

### Patches
Upgrade to Flask-AppBuilder 3.3.4

### For more information
If you have any questions or comments about this advisory:
* Open an issue in https://github.com/dpgaspar/Flask-AppBuilder

## References
- https://github.com/dpgaspar/Flask-AppBuilder/security/advisories/GHSA-m3rf-7m4w-r66q
- https://nvd.nist.gov/vuln/detail/CVE-2021-41265
- https://github.com/dpgaspar/Flask-AppBuilder/commit/eba517aab121afa3f3f2edb011ec6bc4efd61fbc
- https://github.com/dpgaspar/Flask-AppBuilder
- https://github.com/dpgaspar/Flask-AppBuilder/releases/tag/v3.3.4
- https://github.com/pypa/advisory-database/tree/main/vulns/flask-appbuilder/PYSEC-2021-851.yaml
