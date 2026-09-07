# [M] Citizen skin vulnerable to stored XSS through multiple system messages

## Summary
Severity: Medium
Advisory: GHSA-4c2h-67qq-vm87
CVE: CVE-2025-49575
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-06-11
Source: https://github.com/advisories/GHSA-4c2h-67qq-vm87
Type: github-advisory

## Affected
- Packagist: `starcitizentools/citizen-skin` — affected >=2.4.2 <3.3.1

## Details
### Summary
Multiple system messages are inserted into the CommandPaletteFooter as raw HTML, allowing anybody who can edit those messages to insert arbitrary HTML into the DOM.

### Details
The messages are retrieved using the `plain()` output mode: https://github.com/StarCitizenTools/mediawiki-skins-Citizen/blob/072e4365e9084e4b153eac62d3666566c06f5a49/resources/skins.citizen.commandPalette/components/CommandPaletteFooter.vue#L61-L66
`currentTip` is set to one of these messages: https://github.com/StarCitizenTools/mediawiki-skins-Citizen/blob/072e4365e9084e4b153eac62d3666566c06f5a49/resources/skins.citizen.commandPalette/components/CommandPaletteFooter.vue#L69
`currentTip` is inserted as raw HTML (`vue/no-v-html` should *not* be ignored here): https://github.com/StarCitizenTools/mediawiki-skins-Citizen/blob/072e4365e9084e4b153eac62d3666566c06f5a49/resources/skins.citizen.commandPalette/components/CommandPaletteFooter.vue#L3-L4

### PoC
1. Edit `citizen-command-palette-tip-commands`, `citizen-command-palette-tip-users`, `citizen-command-palette-tip-namespace` and `citizen-command-palette-tip-templates` to `<img src="" onerror="alert(1)">` (script tags don't work here due to the way the HTML is inserted)
2. Open the command palette
![image](https://github.com/user-attachments/assets/f07b238b-1ac1-4781-8d03-db755ba04546)

### Impact
This impacts wikis where a group has the `editinterface` but not the `editsitejs` user right.

## References
- https://github.com/StarCitizenTools/mediawiki-skins-Citizen/security/advisories/GHSA-4c2h-67qq-vm87
- https://nvd.nist.gov/vuln/detail/CVE-2025-49575
- https://github.com/StarCitizenTools/mediawiki-skins-Citizen/commit/4fa69e1d062dca7e407cc0530cf1da3e2baaf0b5
- https://github.com/StarCitizenTools/mediawiki-skins-Citizen/commit/54c8717d45ce1594918f11cb9ce5d0ccd8dfee65
- https://github.com/StarCitizenTools/mediawiki-skins-Citizen/commit/93c36ac778397e0e7c46cf7adb1e5d848265f1bd
- https://github.com/StarCitizenTools/mediawiki-skins-Citizen
