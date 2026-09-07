# [M] Logic error in dolibarr/dolibarr

## Summary
Severity: Medium
Advisory: GHSA-8vq6-5f66-hp3r
CVE: CVE-2022-0746
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-02-26
Source: https://github.com/advisories/GHSA-8vq6-5f66-hp3r
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0 <16.0

## Details
In dolibarr/dolibarr prior to 16.0 any low privileged users could update their login name which should only be updated by admin.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0746
- https://github.com/dolibarr/dolibarr/commit/4973019630d51ad76b7c1a4141ec7a33053a7d21
- https://github.com/dolibarr/dolibarr
- https://huntr.dev/bounties/b812ea22-0c02-46fe-b89f-04519dfb1ebd
