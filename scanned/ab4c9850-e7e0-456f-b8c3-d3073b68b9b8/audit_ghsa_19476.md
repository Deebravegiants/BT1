# [H] ezsystems/ezplatform-richtext allows access to external entities in XML

## Summary
Severity: High
Advisory: GHSA-2jqj-5qv2-xvcg
CWE: CWE-611
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-04-10
Source: https://github.com/advisories/GHSA-2jqj-5qv2-xvcg
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezplatform-richtext` — affected >=2.3.0-beta1 <2.3.26

## Details
### Impact
This security advisory resolves a vulnerability in the RichText field type. By entering a maliciously crafted input into the RichText XML, an attacker could perform an attack using XML external entity (XXE) injection, which might be able to read files on the server. To exploit this vulnerability the attacker would need to already have edit permission to content with RichText fields, which typically means Editor role or higher. The fix removes unsafe elements from XML code, while preserving safe elements.

If you have a stored XXE attack in your content drafts, the fix prevents it from extracting data both during editing and preview. However, if such an attack has already been published and the result is stored in the content, it is unfortunately not possible to detect and remove it by automatic means.

### Credits
This vulnerability was discovered and reported to Ibexa by Dennis Henke, Thorsten Niephaus, Marat Aytuganov, and Stephan Sekula of [Compass Security Deutschland GmbH](https://www.compass-security.com/en/). We thank them for reporting it responsibly to us.

### Patches
- See "Patched versions"
- https://github.com/ezsystems/ezplatform-richtext/commit/5ba2a82cc3aa6235ecfe87278e20c1451d9df913

### Workarounds
- Exploitation requires edit access to RichText content. If you can trust your editors, and you don't grant edit permission to any externals, you are not at risk in practice.

### References
- https://developers.ibexa.co/security-advisories/ibexa-sa-2025-002-xxe-vulnerability-in-richtext

## References
- https://github.com/ezsystems/ezplatform-richtext/security/advisories/GHSA-2jqj-5qv2-xvcg
- https://github.com/ezsystems/ezplatform-richtext/commit/5ba2a82cc3aa6235ecfe87278e20c1451d9df913
- https://developers.ibexa.co/security-advisories/ibexa-sa-2025-002-xxe-vulnerability-in-richtext
- https://github.com/ezsystems/ezplatform-richtext
