# [H] Server side request forgery in LiveHelperChat

## Summary
Severity: High
Advisory: GHSA-hhr9-7xvh-8xgc
CVE: CVE-2022-1213
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2022-04-06
Source: https://github.com/advisories/GHSA-hhr9-7xvh-8xgc
Type: github-advisory

## Affected
- Packagist: `remdex/livehelperchat` — affected >=0 <3.67

## Details
SSRF filter bypass port 80, 433 in LiveHelperChat prior to v3.67. An attacker could make the application perform arbitrary requests, bypass CVE-2022-1191

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1213
- https://github.com/LiveHelperChat/livehelperchat/issues/1752
- https://github.com/livehelperchat/livehelperchat/commit/abc9599ee7aded466ca216741dcaea533c908111
- https://github.com/livehelperchat/livehelperchat
- https://huntr.dev/bounties/084387f6-5b9c-4017-baa2-5fcf65b051e1
