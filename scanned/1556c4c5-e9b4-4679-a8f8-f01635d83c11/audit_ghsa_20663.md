# [M] Microweber's title parameter in the body of POST request vulnerable to stored XSS

## Summary
Severity: Medium
Advisory: GHSA-cf6r-q678-f2p7
CVE: CVE-2022-2777
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2022-08-12
Source: https://github.com/advisories/GHSA-cf6r-q678-f2p7
Type: github-advisory

## Affected
- Packagist: `microweber/microweber` — affected >=0 <1.3.1

## Details
In Microweber prior to v1.3.1, the title parameter in the body of POST request when creating/editing a category is vulnerable to stored cross-site scripting.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2777
- https://github.com/microweber/microweber/commit/60eef7494211d1c458228c321e986edeaa401a58
- https://github.com/microweber/microweber
- https://huntr.dev/bounties/13dd2f4d-0c7f-483e-a771-e1ed2ff1c36f
