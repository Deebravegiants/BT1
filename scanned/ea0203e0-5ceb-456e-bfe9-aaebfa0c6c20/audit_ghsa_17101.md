# [M] Potential log injection in reset user endpoint in CKAN

## Summary
Severity: Medium
Advisory: GHSA-8g38-3m6v-232j
CVE: CVE-2024-27097
CWE: CWE-117, CWE-532
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-03-13
Source: https://github.com/advisories/GHSA-8g38-3m6v-232j
Type: github-advisory

## Affected
- PyPI: `ckan` — affected >=0 <2.9.11
- PyPI: `ckan` — affected >=2.10.0 <2.10.4

## Details
A user endpoint didn't perform filtering on an incoming parameter, which was added directly to the application log. This could lead to an attacker injecting false log entries or corrupt the log file format.

### Patches
This has been fixed in the CKAN 2.9.11 and 2.10.4 versions

### Workarounds
Override the `/user/reset` endpoint to filter the `id` parameter in order to exclude newlines

## References
- https://github.com/ckan/ckan/security/advisories/GHSA-8g38-3m6v-232j
- https://nvd.nist.gov/vuln/detail/CVE-2024-27097
- https://github.com/ckan/ckan/commit/5fa133e7e9019573066455b5d442e93c62b3fc93
- https://github.com/ckan/ckan/commit/81b56c55e5e3651d7fcf9642cd5a489a9b62212c
- https://github.com/ckan/ckan/commit/d81f411bff2da7347c343a83e17f5814475b5b64
- https://docs.ckan.org/en/2.10/changelog.html#v-2-10-4-2024-03-13
- https://github.com/ckan/ckan
