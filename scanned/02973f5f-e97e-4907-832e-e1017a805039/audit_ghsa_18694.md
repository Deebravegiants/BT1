# [M] Citizen vulnerable to stored XSS in sticky header button messages

## Summary
Severity: Medium
Advisory: GHSA-g955-vw6w-v6pp
CVE: CVE-2025-62508
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-10-20
Source: https://github.com/advisories/GHSA-g955-vw6w-v6pp
Type: github-advisory

## Affected
- Packagist: `starcitizentools/citizen-skin` — affected >=3.3.0 <3.9.0

## Details
### Summary
The JS implementation for copying button labels to the sticky header in the Citizen skin unescapes HTML characters, allowing for stored XSS through system messages.

### Details
In the `copyButtonAttributes` function in `stickyHeader.js`, when copying the button labels, the `innerHTML` of the new element is set to the `textContent` of the old element:
https://github.com/StarCitizenTools/mediawiki-skins-Citizen/blob/f4cbcecf5aca0ae69966b23d4983f9cb5033f319/resources/skins.citizen.scripts/stickyHeader.js#L29-L41
This unescapes any escaped HTML characters and causes the contents of the system messages to be interpreted as HTML.

### PoC
1. Edit any of the affected messages (`citizen-share`, `citizen-view-history`, `citizen-view-edit`, `nstab-talk`) to the following payload: `<img src="" onerror="alert('Sticky Header Button XSS')">`.
2. Visit any mainpage article in the wiki using the Citizen skin.

<img width="495" height="228" alt="image" src="https://github.com/user-attachments/assets/ac75b8e1-b181-4335-9526-17d6b6f8518e" />
<img width="569" height="157" alt="image" src="https://github.com/user-attachments/assets/c052edb9-ff68-4869-9c66-3ec85e7ff68a" />


### Impact
This impacts wikis where a group has the `editinterface` but not the `editsitejs` user right. By default, this is the case for the `sysop` group.

## References
- https://github.com/StarCitizenTools/mediawiki-skins-Citizen/security/advisories/GHSA-g955-vw6w-v6pp
- https://nvd.nist.gov/vuln/detail/CVE-2025-62508
- https://github.com/StarCitizenTools/mediawiki-skins-Citizen/commit/e006923c6dbf113c9a025ca186ecc09fe7b93a15
- https://github.com/StarCitizenTools/mediawiki-skins-Citizen/commit/fbb1d4fe9627281567706f3f6fc99a42ce16fdc4
- https://github.com/StarCitizenTools/mediawiki-skins-Citizen
