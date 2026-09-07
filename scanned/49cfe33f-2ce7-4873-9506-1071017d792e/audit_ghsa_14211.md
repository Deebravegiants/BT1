# [M] Directus API vulnerable to denial of service

## Summary
Severity: Medium
Advisory: GHSA-3gvp-54v2-2jrp
CVE: CVE-2020-19850
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-04-04
Source: https://github.com/advisories/GHSA-3gvp-54v2-2jrp
Type: github-advisory

## Affected
- npm: `directus` — affected >=2.2.0 <2.2.1

## Details
An issue found in Directus API v.2.2.0 allows a remote attacker to cause a denial of service via a great amount of HTTP requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-19850
- https://github.com/directus/api/issues/982
- https://github.com/directus/v8-archive
