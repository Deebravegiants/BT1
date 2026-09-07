# [M] starcitizentools/citizen-skin allows stored XSS in search no result messages

## Summary
Severity: Medium
Advisory: GHSA-86xf-2mgp-gv3g
CVE: CVE-2025-49576
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-06-13
Source: https://github.com/advisories/GHSA-86xf-2mgp-gv3g
Type: github-advisory

## Affected
- Packagist: `starcitizentools/citizen-skin` — affected >=2.31.0 <3.3.1

## Details
### Summary
The `citizen-search-noresults-title` and `citizen-search-noresults-desc` system messages are inserted into raw HTML, allowing anybody who can edit those messages to insert arbitrary HTML into the DOM.

### Details
The system messages are inserted as raw HTML by the mustache template:
https://github.com/StarCitizenTools/mediawiki-skins-Citizen/blob/407052e7069bdeae927d6f1a2a1c9a45b473bf9a/resources/skins.citizen.search/templates/TypeaheadPlaceholder.mustache#L8-L9


### PoC
1. Edit `citizen-search-noresults-title` and `citizen-search-noresults-desc` to `<img src="" onerror="alert('citizen-search-noresults-title')">` and `<img src="" onerror="alert('citizen-search-noresults-desc')">` (script tags don't work here due to the way the HTML is inserted)
2. Open the search bar and search for a page that doesn't exist to get the "no results" messages to show up

![image](https://github.com/user-attachments/assets/cf2963bc-5c86-4a4d-8574-de92d89d6d81)
![image](https://github.com/user-attachments/assets/44839a7e-c08c-4df9-bd84-0f5863f64163)


### Impact
This impacts wikis where a group has the `editinterface` but not the `editsitejs` user right.

## References
- https://github.com/StarCitizenTools/mediawiki-skins-Citizen/security/advisories/GHSA-86xf-2mgp-gv3g
- https://nvd.nist.gov/vuln/detail/CVE-2025-49576
- https://github.com/StarCitizenTools/mediawiki-skins-Citizen/commit/93c36ac778397e0e7c46cf7adb1e5d848265f1bd
- https://github.com/StarCitizenTools/mediawiki-skins-Citizen/commit/a0296afaedbe1a277337a2d8f1da83cb3a79b9ab
- https://github.com/StarCitizenTools/mediawiki-skins-Citizen
