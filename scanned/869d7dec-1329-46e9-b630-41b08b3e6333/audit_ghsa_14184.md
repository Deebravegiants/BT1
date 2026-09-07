# [M] Silverstripe Form Capture vulnerable to stored cross-site-scripting

## Summary
Severity: Medium
Advisory: GHSA-38h6-gmr2-j4wx
CVE: CVE-2023-28851
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-04-03
Source: https://github.com/advisories/GHSA-38h6-gmr2-j4wx
Type: github-advisory

## Affected
- Packagist: `bigfork/silverstripe-form-capture` — affected >=3.0.0 <3.1.1
- Packagist: `andrewhaine/silverstripe-form-capture` — affected >=0.2.0 <1.0.2
- Packagist: `andrewhaine/silverstripe-form-capture` — affected >=2.0.0 <2.2.5
- Packagist: `andrewhaine/silverstripe-form-capture` — affected >=1.0.0 <1.0.2

## Details
### Impact
Improper escaping when presenting stored form submissions allowed for an attacker to perform a Cross-Site Scripting attack

### Patches
The vulnerability was initially patched in version 1.0.2, and version 1.1.0 includes this patch. The bug was then accidentally re-introduced during a merge error, and has been re-patched in versions 2.2.5 and 3.1.1.

## References
- https://github.com/bigfork/silverstripe-form-capture/security/advisories/GHSA-38h6-gmr2-j4wx
- https://nvd.nist.gov/vuln/detail/CVE-2023-28851
- https://github.com/bigfork/silverstripe-form-capture/commit/3a7a3c480e3fccddce9c5f359796d45a8302a622
- https://github.com/bigfork/silverstripe-form-capture/commit/5b3aa39dd1eef042f173167b0fa4d3f717971772
- https://github.com/bigfork/silverstripe-form-capture
