# [M] Passbolt Api Tabnabbing when opening URI with menu "Open URI in a new tab"

## Summary
Severity: Medium
Advisory: GHSA-qm5v-pj64-852j
CWE: CWE-657
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-05-20
Source: https://github.com/advisories/GHSA-qm5v-pj64-852j
Type: github-advisory

## Affected
- Packagist: `passbolt/passbolt_api` — affected >=0 <2.11.0

## Details
### Description
A user could create and share a resource with a malicious URI. When the victim opens with menu “Open URI in a new tab” function, the malicious page has access to the window.opener object.

### Impact of issue
The newly opened malicious page can for example change the window.opener.location to redirect the user to a phishing page, or call a JavaScript function served by the AppJS on the user behalf for example to try to affect the integrity of the data.

### Fix
The code that opens a new window via window.open(); now open the tab with the noopener attribute.

## References
- https://github.com/passbolt/passbolt_api/commit/f568e113beb3134446eda9e66400d28d726ee20d
- https://github.com/FriendsOfPHP/security-advisories/blob/master/passbolt/passbolt_api/2019-08-07-3.yaml
- https://github.com/passbolt/passbolt_api
- https://www.passbolt.com/incidents/20190807_multiple_vulnerabilities
