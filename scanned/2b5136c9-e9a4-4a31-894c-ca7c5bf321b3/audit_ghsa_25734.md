# [H] Denial of service in microweber

## Summary
Severity: High
Advisory: GHSA-hrf4-hcpc-3345
CVE: CVE-2022-0961
CWE: CWE-190
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-16
Source: https://github.com/advisories/GHSA-hrf4-hcpc-3345
Type: github-advisory

## Affected
- Packagist: `microweber/microweber` — affected >=0

## Details
Microweber is drag and drop website builder and CMS with E-commerce. The microweber prior 1.2.12 application allows large characters to insert in the input field "post title" which can allow attackers to cause a Denial of Service (DoS) via a crafted HTTP request. The post title input can be limited to 500 characters or max 1000 characters as a workaround.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0961
- https://github.com/microweber/microweber/commit/f7acbd075dff4825b35b597b74958de9edce67fc
- https://github.com/microweber/microweber
- https://huntr.dev/bounties/cdf00e14-38a7-4b6b-9bb4-3a71bf24e436
