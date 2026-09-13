# [H] Information exposure in elgg

## Summary
Severity: High
Advisory: GHSA-hx6g-q9v2-xh7v
CVE: CVE-2021-3980
CWE: CWE-359
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-12-16
Source: https://github.com/advisories/GHSA-hx6g-q9v2-xh7v
Type: github-advisory

## Affected
- Packagist: `elgg/elgg` — affected >=0 <3.3.23
- Packagist: `elgg/elgg` — affected >=4.0.0 <4.0.5

## Details
elgg is vulnerable to Exposure of Private Personal Information to an Unauthorized Actor. Forms in the view namespace 'forms/admin' were not protected by an AdminGatekeeper in case of AJAX requests to 'ajax/form/admin/'.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3980
- https://github.com/Elgg/Elgg/pull/13791
- https://github.com/elgg/elgg/commit/572d210e2392f1fdf47ff2f38665372a6535c126
- https://github.com/Elgg/Elgg
- https://huntr.dev/bounties/1f43f11e-4bd8-451f-a244-dc9541cdc0ac
