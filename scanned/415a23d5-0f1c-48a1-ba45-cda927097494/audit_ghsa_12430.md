# [M] Business Logic Errors in microweber/microweber

## Summary
Severity: Medium
Advisory: GHSA-qjfx-fvx7-3wvw
CVE: CVE-2023-6832
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2023-12-15
Source: https://github.com/advisories/GHSA-qjfx-fvx7-3wvw
Type: github-advisory

## Affected
- Packagist: `microweber/microweber` — affected >=0 <2.0.0

## Details
A vulnerability has been identified in microweber where users can purchase items with a coupon code. If the admin disables the use of the coupon code functionality, but the user sends requests to the API that handles the coupon code, the user can exploit the vulnerability and obtain items at a lower price.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-6832
- https://github.com/microweber/microweber/commit/890e9838aabbc799ebefcf6b20ba25e0fd6dbfee
- https://github.com/microweber/microweber
- https://huntr.com/bounties/53105a20-f4b1-45ad-a734-0349de6d7376
