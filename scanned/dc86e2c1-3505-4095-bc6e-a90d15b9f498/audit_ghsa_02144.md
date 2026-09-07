# [H] Improper Resource Shutdown or Release in TYPO3 extension

## Summary
Severity: High
Advisory: GHSA-34jq-548x-m2x9
CVE: CVE-2021-38623
CWE: CWE-404
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H/E:F/RL:O/RC:C (CVSS_V3)
Published: 2021-08-30
Source: https://github.com/advisories/GHSA-34jq-548x-m2x9
Type: github-advisory

## Affected
- Packagist: `webcoast/deferred-image-processing` — affected >=0 <1.0.2

## Details
Wrong usage of the TYPO3 FAL API results in copies of processed files being saved to the /var/transient/ folder of a TYPO3 website on every frontend request. This  can result in Denial of Service, since the webspace may be filled up with image files simply by crafting a large amount of requests to the website.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-38623
- https://github.com/webcoast-dk/deferred-image-processing
- https://typo3.org/security/advisory/typo3-ext-sa-2021-009
