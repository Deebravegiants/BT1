# [H] Integer Overflow in microweber

## Summary
Severity: High
Advisory: GHSA-5fxv-xx5p-g2fv
CVE: CVE-2022-0968
CWE: CWE-190
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:L/AC:H/PR:H/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-16
Source: https://github.com/advisories/GHSA-5fxv-xx5p-g2fv
Type: github-advisory

## Affected
- Packagist: `microweber/microweber` — affected >=0

## Details
Microweber is a new generation CMS with drag and drop. The microweber application allows large characters to insert in the input field "first & last name" which can allow attackers to cause a Denial of Service (DoS) via a crafted HTTP request. The first name & last name input should be limited to 50 characters or max 100 characters

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0968
- https://github.com/microweber/microweber/commit/80e39084729a57dfe749626c3b9d35247a14c49e
- https://github.com/microweber/microweber
- https://huntr.dev/bounties/97e36678-11cf-42c6-889c-892d415d9f9e
