# [M] CKAN may leak Solr credentials via error message in package_search action

## Summary
Severity: Medium
Advisory: GHSA-2rqw-cfhc-35fh
CVE: CVE-2024-41674
CWE: CWE-209
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-08-21
Source: https://github.com/advisories/GHSA-2rqw-cfhc-35fh
Type: github-advisory

## Affected
- PyPI: `ckan` — affected >=2.0.0 <2.10.5

## Details
If there were connection issues with the Solr server, the internal Solr URL (potentially including credentials) could be leaked to `package_search` calls as part of the returned error message

### Patches
This has been patched in CKAN 2.10.5 and 2.11.0

## References
- https://github.com/ckan/ckan/security/advisories/GHSA-2rqw-cfhc-35fh
- https://nvd.nist.gov/vuln/detail/CVE-2024-41674
- https://github.com/ckan/ckan/commit/f6b032cd7082d784938165bbd113557639002ca7
- https://github.com/ckan/ckan
