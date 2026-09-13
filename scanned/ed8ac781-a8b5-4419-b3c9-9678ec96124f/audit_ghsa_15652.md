# [M] adolph_dudu ratio-swiper was discovered to contain a prototype pollution via the function extendDefaults

## Summary
Severity: Medium
Advisory: GHSA-88vr-hjqx-57qh
CVE: CVE-2024-38997
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-07-01
Source: https://github.com/advisories/GHSA-88vr-hjqx-57qh
Type: github-advisory

## Affected
- npm: `@adolph_dudu/ratio-swiper` — affected 0.0.2

## Details
adolph_dudu ratio-swiper v0.0.2 was discovered to contain a prototype pollution via the function extendDefaults. This vulnerability allows attackers to execute arbitrary code or cause a Denial of Service (DoS) via injecting arbitrary properties.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-38997
- https://gist.github.com/mestrtee/840f5d160aab4151bd0451cfb822e6b5
- https://github.com/Adophlidu/swiper
