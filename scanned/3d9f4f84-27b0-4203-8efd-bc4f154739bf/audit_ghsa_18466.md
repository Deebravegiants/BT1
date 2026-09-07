# [H] starcitizentools/citizen-skin is vulnerable to Stored XSS attack in the legacy search bar through page descriptions

## Summary
Severity: High
Advisory: GHSA-rq6g-6g94-jfr4
CVE: CVE-2025-53368
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2025-07-03
Source: https://github.com/advisories/GHSA-rq6g-6g94-jfr4
Type: github-advisory

## Affected
- Packagist: `starcitizentools/citizen-skin` — affected >=1.9.4 <3.4.0

## Details
### Summary
Page descriptions are inserted into raw HTML without proper sanitization by the Citizen skin when using the old search bar.

### Details

The descriptions, which are unsanitized, are inserted as raw HTML:
https://github.com/StarCitizenTools/mediawiki-skins-Citizen/blob/d4dfc3697a82948b3b9c4d44e9a273c79bc86b87/resources/skins.citizen.search/templates/TypeaheadListItem.mustache#L18

### PoC


All of the reproduction methods require the command palette to be disabled via `$wgCitizenEnableCommandPalette = false;`.
Additionally, the action API must be used as the Search Gateway via  `$wgCitizenSearchGateway = 'mwActionApi';`.


#### TextExtracts as the description source

* Enable the TextExtracts extension
* Add `$wgCitizenSearchDescriptionSource = 'textextracts';` to your LocalSettings.php
* Create a page called `CitizenXSSTextExtracts` and insert `<img src="" onerror="alert('citizen search xss')">` into it
* Open the search modal and search for `CitizenXSSTextExtracts`

![image](https://github.com/user-attachments/assets/fbc88458-c429-4f08-9376-584b7db93f58)


#### Description2 as the description source

* Enable the Description2 extension
* Add `$wgEnableMetaDescriptionFunctions = true;` to your LocalSettings.php to enable the `{{#description2:}}` parser function
* Add `$wgCitizenSearchDescriptionSource = 'pagedescription';` to your LocalSettings.php
* Create a page called `CitizenXSSDescription2` and insert `{{#description2:<img src="" onerror="alert('citizen search xss 2')">}}` into it
* Open the search modal and search for `CitizenXSSDescription2`

![image](https://github.com/user-attachments/assets/24513eba-dbec-4bc6-ac06-6276d509fcab)


#### Wikibase as the description source

Note that this method is currently untested due to issues I experienced when setting up Wikibase.

* Enable Wikibase client + repo in your wiki
* Add `$wgCitizenSearchDescriptionSource = 'wikidata';` to your LocalSettings.php
* Have an item with a description like `<img src="" onerror="alert('citizen search xss 3')">`
* Open the search modal and search for the page linked to the item


#### ShortDescription as the description source

* Enable the ShortDescription extension
* Add `$wgCitizenSearchDescriptionSource = 'wikidata';` to your LocalSettings.php
* Create a page called `CitizenXSSDescription4` and insert `{{SHORTDESC:<img src="" onerror="alert('citizen search xss 4')">}}` into it
* Open the search modal and search for `CitizenXSSDescription4`

### Impact

On all wikis that use the aforementioned settings (command palette disabled or using an old release where the old search bar is still used; using the action API as the search gateway), anybody who can edit pages is able to insert XSS payloads into the DOM for other users who are searching for specific pages.

## References
- https://github.com/StarCitizenTools/mediawiki-skins-Citizen/security/advisories/GHSA-rq6g-6g94-jfr4
- https://nvd.nist.gov/vuln/detail/CVE-2025-53368
- https://github.com/StarCitizenTools/mediawiki-skins-Citizen/commit/aedbceb3380bb48db6b59e272fc187529c71c8ca
- https://github.com/StarCitizenTools/mediawiki-skins-Citizen
- https://github.com/StarCitizenTools/mediawiki-skins-Citizen/releases/tag/v3.4.0
