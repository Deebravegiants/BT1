# [M] Directus: Open Redirect in Admin 2FA Setup Page

## Summary
Severity: Medium
Advisory: GHSA-q75c-4gmv-mg9x
CVE: CVE-2026-35411
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-04-04
Source: https://github.com/advisories/GHSA-q75c-4gmv-mg9x
Type: github-advisory

## Affected
- npm: `directus` — affected >=0 <11.16.1

## Details
### Summary

Directus is vulnerable to an Open Redirect via the redirect query parameter on the `/admin/tfa-setup` page. When an administrator who has not yet configured Two-Factor Authentication (2FA) visits a crafted URL, they are presented with the legitimate Directus 2FA setup page. After completing the setup process, the application redirects the user to the attacker-controlled URL specified in the `redirect` parameter without any validation.

This vulnerability could be used in phishing attacks targeting Directus administrators, as the initial interaction occurs on a trusted domain.

### Credits
Discovered by Neo by ProjectDiscovery (https://neo.projectdiscovery.io/)

## References
- https://github.com/directus/directus/security/advisories/GHSA-q75c-4gmv-mg9x
- https://nvd.nist.gov/vuln/detail/CVE-2026-35411
- https://github.com/directus/directus
