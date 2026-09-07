# [M] Pimcore Admin Classic Bundle Cross-site Scripting (XSS) in PDF previews

## Summary
Severity: Medium
Advisory: GHSA-jfxw-6c5v-c42f
CVE: CVE-2023-46722
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-11-01
Source: https://github.com/advisories/GHSA-jfxw-6c5v-c42f
Type: github-advisory

## Affected
- Packagist: `pimcore/admin-ui-classic-bundle` — affected >=0 <1.2.0

## Details
### Impact
This vulnerability has the potential to steal a user's cookie and gain unauthorized access to that user's account through the stolen cookie or redirect users to other malicious sites.

Proof of Concept
Step 1. Go to /admin and login.
Step 2. In Documents, go to home -> click on Sample Content -> click Document folder
Step 3. Upload file PDF content XSS payload

### Patches
Apply patches 
https://github.com/pimcore/pimcore/commit/757375677dc83a44c6c22f26d97452cc5cda5d7c.patch
https://github.com/pimcore/admin-ui-classic-bundle/commit/19fda2e86557c2ed4978316104de5ccdaa66d8b9.patch

### Workarounds
Update to version 1.2.0 or apply patches manually
https://github.com/pimcore/pimcore/commit/757375677dc83a44c6c22f26d97452cc5cda5d7c.patch
https://github.com/pimcore/admin-ui-classic-bundle/commit/19fda2e86557c2ed4978316104de5ccdaa66d8b9.patch

## References
- https://github.com/pimcore/admin-ui-classic-bundle/security/advisories/GHSA-jfxw-6c5v-c42f
- https://nvd.nist.gov/vuln/detail/CVE-2023-46722
- https://github.com/pimcore/admin-ui-classic-bundle/commit/19fda2e86557c2ed4978316104de5ccdaa66d8b9
- https://github.com/pimcore/pimcore/commit/757375677dc83a44c6c22f26d97452cc5cda5d7c
- https://github.com/pimcore/admin-ui-classic-bundle
