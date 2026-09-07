# [H] Magento LTS vulnerable to Stored XSS via TinyMCE WYSIWYG Editor

## Summary
Severity: High
Advisory: GHSA-9j5w-2cqc-cwj9
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2023-12-08
Source: https://github.com/advisories/GHSA-9j5w-2cqc-cwj9
Type: github-advisory

## Affected
- Packagist: `openmage/magento-lts` — affected >=0 <20.2.0

## Details
From HackerOne report [#1948040](https://hackerone.com/reports/1948040) by Halit AKAYDIN (hltakydn)

### Impact
_What kind of vulnerability is it? Who is impacted?_

The TinyMCE WYSIWYG editor fails to filter scripts when rendering the HTML in specially crafted HTML tags.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

This vulnerability was fixed in version 20.2.0 by upgrading TinyMCE to a recent version in https://github.com/OpenMage/magento-lts/pull/3220

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

The WYSIWYG editor features could be disabled in the configuration. Possibly some WAF appliances would filter this attack.

### References
_Are there any links users can visit to find out more?_

The attack is simply an exploit of the "onmouseover" attribute of an `img` element as described on [OWASP XSS Filter Evasion](https://cheatsheetseries.owasp.org/cheatsheets/XSS_Filter_Evasion_Cheat_Sheet.html)

## References
- https://github.com/OpenMage/magento-lts/security/advisories/GHSA-9j5w-2cqc-cwj9
- https://github.com/OpenMage/magento-lts/pull/3220
- https://hackerone.com/reports/1948040
- https://github.com/OpenMage/magento-lts
- https://github.com/OpenMage/magento-lts/releases/tag/v20.2.0
