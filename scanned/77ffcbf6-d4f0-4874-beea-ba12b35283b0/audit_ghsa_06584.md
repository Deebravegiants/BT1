# [M] GeoNode: Stored XSS to full account takeover

## Summary
Severity: Medium
Advisory: GHSA-rwcv-whm8-fmxm
CVE: CVE-2024-27091
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-13
Source: https://github.com/advisories/GHSA-rwcv-whm8-fmxm
Type: github-advisory

## Affected
- PyPI: `geonode` — affected >=3.2.1 <4.2.3

## Details
An issue exists within GEONODE where the current rich text editor is vulnerable to Stored XSS. The applications cookies are set securely, but it is possible to retrieve a victims CSRF token and issue a request to change another user's email address to perform a full account takeover. Due to the script element not impacting the CORS policy, requests will succeed.

## References
- https://github.com/GeoNode/geonode/security/advisories/GHSA-rwcv-whm8-fmxm
- https://nvd.nist.gov/vuln/detail/CVE-2024-27091
- https://github.com/GeoNode/geonode/commit/e53bdeff331f4b577918927d60477d4b50cca02f
- https://github.com/GeoNode/geonode
- https://github.com/pypa/advisory-database/tree/main/vulns/geonode/PYSEC-2024-320.yaml
