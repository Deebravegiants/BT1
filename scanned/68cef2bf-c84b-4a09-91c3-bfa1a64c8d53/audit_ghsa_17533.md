# [M] starcitizentools/citizen-skin allows stored XSS in preference menu heading messages

## Summary
Severity: Medium
Advisory: GHSA-jwr7-992g-68mh
CVE: CVE-2025-49577
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-06-13
Source: https://github.com/advisories/GHSA-jwr7-992g-68mh
Type: github-advisory

## Affected
- Packagist: `starcitizentools/citizen-skin` — affected >=2.13.0 <3.3.1

## Details
### Summary
Various preferences messages are inserted into raw HTML, allowing anybody who can edit those messages to insert arbitrary HTML into the DOM.

### Details
The `innerHtml` of the label div is set to the `textContent` of the label, essentially unsanitizing the system messages:
https://github.com/StarCitizenTools/mediawiki-skins-Citizen/blob/407052e7069bdeae927d6f1a2a1c9a45b473bf9a/resources/skins.citizen.preferences/addPortlet.polyfill.js#L18


### PoC
1. Edit `citizen-feature-custom-font-size-name` (or any other message displayed in a heading in the preferences menu) to `<img src="" onerror="alert('citizen-feature-custom-font-size-name')">` (script tags don't work here due to the way the HTML is inserted)
2. Open the preferences menu
![image](https://github.com/user-attachments/assets/b75f100d-09cc-443c-b635-e9d6ab48d133)

## References
- https://github.com/StarCitizenTools/mediawiki-skins-Citizen/security/advisories/GHSA-jwr7-992g-68mh
- https://nvd.nist.gov/vuln/detail/CVE-2025-49577
- https://github.com/StarCitizenTools/mediawiki-skins-Citizen/commit/93c36ac778397e0e7c46cf7adb1e5d848265f1bd
- https://github.com/StarCitizenTools/mediawiki-skins-Citizen/commit/a741639085d70c22a9f49890542a142a223bf981
- https://github.com/StarCitizenTools/mediawiki-skins-Citizen
