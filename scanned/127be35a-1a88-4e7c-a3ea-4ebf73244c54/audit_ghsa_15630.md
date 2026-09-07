# [M] Magento LTS vulnerable to stored Cross-site Scripting (XSS) in admin system configs

## Summary
Severity: Medium
Advisory: GHSA-5vrp-638w-p8m2
CVE: CVE-2024-41676
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2024-07-29
Source: https://github.com/advisories/GHSA-5vrp-638w-p8m2
Type: github-advisory

## Affected
- Packagist: `openmage/magento-lts` — affected >=0 <20.10.1

## Details
### Impact

This XSS vulnerability is about the system configs
* design/header/welcome
* design/header/logo_src
* design/header/logo_src_small
* design/header/logo_alt

They are intended to enable admins to set a text in the two cases, and to define an image url for the other two cases.
But because of previously missing escaping allowed to input arbitrary html and as a consequence also arbitrary JavaScript.

While this is in most usage scenarios not a relevant issue, some people work with more restrictive roles in the backend. Here the ability to inject JavaScript with these settings would be an unintended and unwanted privilege.

### Patches
_Has the problem been patched? What versions should users upgrade to?_  

The problem is patched with Version 20.10.1 or higher.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_  

Possible mitigations are
* Restricting access to the System Configs 
* checking templates where these settings are used to apply proper html filtering

### For Users relying on this possibility

Some Users might actually rely on the ability to use html there.
You can restore the previous behavior by making use of the new introduced `->getUnescapedValue()` method on this escaped elements. Developers should have a look at the newly introduced `Mage_Core_Model_Security_HtmlEscapedString`

### Credit

Credit goes to  Aakash Adhikari @justlife4x4 for finding this issue

## References
- https://github.com/OpenMage/magento-lts/security/advisories/GHSA-5vrp-638w-p8m2
- https://nvd.nist.gov/vuln/detail/CVE-2024-41676
- https://github.com/OpenMage/magento-lts/commit/484cf8afc550e98bbf2c03fbb29a8450a32e7948
- https://github.com/OpenMage/magento-lts
