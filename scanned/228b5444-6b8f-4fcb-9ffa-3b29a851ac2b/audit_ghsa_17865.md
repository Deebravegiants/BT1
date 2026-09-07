# [M] moonshine Stored Cross-Site Scripting Vulnerability in Create Article

## Summary
Severity: Medium
Advisory: GHSA-p632-58pp-c9xg
CVE: CVE-2025-51487
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-08-19
Source: https://github.com/advisories/GHSA-p632-58pp-c9xg
Type: github-advisory

## Affected
- Packagist: `moonshine/moonshine` — affected >=0 <3.12.4

## Details
A stored cross-site scripting (XSS) vulnerability in the Create Article function of MoonShine v3.12.3 allows attackers to execute arbitrary web scripts or HTML via injecting a crafted payload into the Link parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-51487
- https://github.com/moonshine-software/moonshine/commit/f108f4ea5c0d66e8172c2dc397c1d9a6f466d9c6
- https://github.com/GiacoLenzo2109/MoonShine_Software_PoCs
- https://github.com/moonshine-software/moonshine
