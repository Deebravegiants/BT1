# [C] Formie: Pre-authenticated server-side template injection in Hidden fields

## Summary
Severity: Critical
Advisory: GHSA-x7m9-mwc2-g6w2
CVE: CVE-2026-45697
CWE: CWE-1336, CWE-693, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-x7m9-mwc2-g6w2
Type: github-advisory

## Affected
- Packagist: `verbb/formie` — affected >=3.0.0-beta.1 <3.1.24
- Packagist: `verbb/formie` — affected >=0 <2.2.20

## Details
### Impact
- Unauthenticated users could submit crafted values into Hidden fields (with Default value → Custom) that were evaluated as Twig during submission handling, which could lead to serious compromise of the Craft site (depending on template/sandbox behavior).
- Sites with public Formie forms that include at least one Hidden field with that configuration.
- No CP login for the reported chain.

### Patches
- [2.2.20](https://github.com/verbb/formie/releases/tag/2.2.20), [3.1.24](https://github.com/verbb/formie/releases/tag/3.1.24)

### Workarounds
- Temporarily remove Hidden fields from public forms or switch Hidden default away from Custom where feasible
- Otherwise, upgrade to patched versions

## References
- https://github.com/verbb/formie/security/advisories/GHSA-x7m9-mwc2-g6w2
- https://nvd.nist.gov/vuln/detail/CVE-2026-45697
- https://github.com/verbb/formie/commit/f690d5623163ce2a95da305238d6367575486ee3
- https://github.com/verbb/formie
- https://github.com/verbb/formie/releases/tag/2.2.20
- https://github.com/verbb/formie/releases/tag/3.1.24
