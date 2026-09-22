# [C] elFinder Unrestricted File Upload vulnerability

## Summary
Severity: Critical
Advisory: GHSA-x4jx-hjwf-gc99
CVE: CVE-2021-43421
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-08
Source: https://github.com/advisories/GHSA-x4jx-hjwf-gc99
Type: github-advisory

## Affected
- Packagist: `studio-42/elfinder` — affected >=2.0.4 <2.1.60

## Details
A File Upload vulnerability exists in Studio-42 elFinder 2.0.4 to 2.1.59 via `connector.minimal.php`, which allows a remote malicious user to upload arbitrary files and execute PHP code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-43421
- https://github.com/Studio-42/elFinder/issues/3429
- https://github.com/Studio-42/elFinder/commit/c08bcbfa722d758d01975799b7036951eb5d33cb
- https://github.com/Studio-42/elFinder
- https://twitter.com/infosec_90/status/1455180286354919425
