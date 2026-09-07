# [H] Aimeos GrapesJS CMS extension has possible stored XSS that's exploitable by authenticated editors

## Summary
Severity: High
Advisory: GHSA-424m-fj2q-g7vg
CVE: CVE-2025-66468
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-12-03
Source: https://github.com/advisories/GHSA-424m-fj2q-g7vg
Type: github-advisory

## Affected
- Packagist: `aimeos/ai-cms-grapesjs` — affected >=2021.04.1 <2021.10.8
- Packagist: `aimeos/ai-cms-grapesjs` — affected >=2022.04.1 <2022.10.9
- Packagist: `aimeos/ai-cms-grapesjs` — affected >=2023.04.1 <2023.10.15
- Packagist: `aimeos/ai-cms-grapesjs` — affected >=2024.04.1 <2024.10.8
- Packagist: `aimeos/ai-cms-grapesjs` — affected >=2025.04.1 <2025.10.2

## Details
### Impact

Javascript code can be injected by malicious editors for a stored XSS attack if the standard Content Security Policy is disabled.

### Workaround

If the standard CSP rules are active (default in production mode), an exploit isn't possible.

### Credits

Lwin Min Oo <lwinminoo2244@gmail.com>

## References
- https://github.com/aimeos/ai-cms-grapesjs/security/advisories/GHSA-424m-fj2q-g7vg
- https://nvd.nist.gov/vuln/detail/CVE-2025-66468
- https://github.com/aimeos/ai-cms-grapesjs/commit/2214f71ac27cdea25f11c8adf6bb5816db47a042
- https://github.com/aimeos/ai-cms-grapesjs
