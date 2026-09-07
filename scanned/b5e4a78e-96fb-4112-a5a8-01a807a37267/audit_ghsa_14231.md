# [M] Pimcore Perspective Editor vulnerable to stored cross-site scripting (XSS) in perspective name

## Summary
Severity: Medium
Advisory: GHSA-fq8q-55v3-2986
CVE: CVE-2023-28850
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-04-03
Source: https://github.com/advisories/GHSA-fq8q-55v3-2986
Type: github-advisory

## Affected
- Packagist: `pimcore/perspective-editor` — affected >=0 <1.5.1

## Details
### Impact
This vulnerability has the potential to steal a user's cookie and gain unauthorized access to that user's account through the stolen cookie or redirect users to other malicious sites.

### Patches
Update to version 1.5.1.

### Workarounds
Apply the patch https://github.com/pimcore/perspective-editor/pull/121.patch manually.

## References
- https://github.com/pimcore/perspective-editor/security/advisories/GHSA-fq8q-55v3-2986
- https://nvd.nist.gov/vuln/detail/CVE-2023-28850
- https://github.com/pimcore/perspective-editor/pull/121.patch
- https://github.com/pimcore/perspective-editor
- https://huntr.dev/bounties/5529f51e-e40f-46f1-887b-c9dbebab4f06
