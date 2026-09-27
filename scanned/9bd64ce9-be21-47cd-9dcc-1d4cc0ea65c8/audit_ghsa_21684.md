# [C] Exposure of Resource to Wrong Sphere in Zip-Local

## Summary
Severity: Critical
Advisory: GHSA-wxj7-97fp-j53j
CVE: CVE-2021-23484
CWE: CWE-29, CWE-668
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-01
Source: https://github.com/advisories/GHSA-wxj7-97fp-j53j
Type: github-advisory

## Affected
- npm: `zip-local` — affected >=0 <0.3.5

## Details
The package zip-local before 0.3.5 are vulnerable to Arbitrary File Write via Archive Extraction (Zip Slip) which can lead to an extraction of a crafted file outside the intended extraction directory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23484
- https://github.com/Mostafa-Samir/zip-local/commit/6bb9b59733df379ac168aa705790bd8339b4bf9b
- https://github.com/Mostafa-Samir/zip-local/commit/949446a95a660c0752b1db0c654f0fd619ae6085
- https://github.com/Mostafa-Samir/zip-local
- https://github.com/Mostafa-Samir/zip-local/blob/master/main.js%23L365
- https://snyk.io/vuln/SNYK-JS-ZIPLOCAL-2327477
