# [M] Cross-site Scripting in Pimcore Datahub

## Summary
Severity: Medium
Advisory: GHSA-vc5r-xfc4-4x22
CVE: CVE-2022-0955
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-03-25
Source: https://github.com/advisories/GHSA-vc5r-xfc4-4x22
Type: github-advisory

## Affected
- Packagist: `pimcore/data-hub` — affected >=0 <1.2.4

## Details
Pimcore Datahub prior to 1.2.4 is vulnerable to stored cross-site scripting. An admin user accessing Datahub triggers the attack, which may result in the user's cookie being stolen.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0955
- https://github.com/pimcore/data-hub/commit/15d5b57af2466eebd3bbc531ead5dafa35d0a36e
- https://github.com/pimcore/data-hub
- https://huntr.dev/bounties/708971a6-1e6c-4c51-a411-255caeba51df
