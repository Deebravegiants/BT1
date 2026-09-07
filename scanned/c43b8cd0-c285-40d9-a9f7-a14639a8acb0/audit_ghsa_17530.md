# [M] starcitizentools/citizen-skin allows stored XSS in user registration date message

## Summary
Severity: Medium
Advisory: GHSA-2v3v-3whp-953h
CVE: CVE-2025-49578
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-06-13
Source: https://github.com/advisories/GHSA-2v3v-3whp-953h
Type: github-advisory

## Affected
- Packagist: `starcitizentools/citizen-skin` — affected >=3.3.0 <3.3.1

## Details
### Summary
Various date messages returned by `Language::userDate` are inserted into raw HTML, allowing anybody who can edit those messages to insert arbitrary HTML into the DOM.

### Details
The result of `$this->lang->userDate( $timestamp, $this->user )` returns unescaped values, but is inserted as raw HTML by Citizen:
https://github.com/StarCitizenTools/mediawiki-skins-Citizen/blob/072e4365e9084e4b153eac62d3666566c06f5a49/includes/Components/CitizenComponentUserInfo.php#L55-L60

### PoC
1. Go to any page using citizen with the uselang parameter set to x-xss and while being logged in
Depending on the registration date of the account you're logged in with, various messages can be shown. In my case, it's `november`:
![image](https://github.com/user-attachments/assets/252a3453-99c8-4ce1-b6d6-a8485b7a9a43)


### Impact
This impacts wikis where a group has the `editinterface` but not the `editsitejs` user right.

## References
- https://github.com/StarCitizenTools/mediawiki-skins-Citizen/security/advisories/GHSA-2v3v-3whp-953h
- https://nvd.nist.gov/vuln/detail/CVE-2025-49578
- https://github.com/StarCitizenTools/mediawiki-skins-Citizen/commit/64cb5d7ab3a6dc0381fae54b31e8fc4afadc8beb
- https://github.com/StarCitizenTools/mediawiki-skins-Citizen/commit/93c36ac778397e0e7c46cf7adb1e5d848265f1bd
- https://github.com/StarCitizenTools/mediawiki-skins-Citizen
