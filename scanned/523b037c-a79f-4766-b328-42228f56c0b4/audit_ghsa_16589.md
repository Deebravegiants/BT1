# [M] TYPO3 vulnerable to an Uncontrolled Resource Consumption in the ShowImageController

## Summary
Severity: Medium
Advisory: GHSA-36g8-62qv-5957
CVE: CVE-2024-34358
CWE: CWE-200, CWE-347, CWE-400
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-05-14
Source: https://github.com/advisories/GHSA-36g8-62qv-5957
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.48
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.45
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.5.37
- Packagist: `typo3/cms-core` — affected >=12.0.0 <12.4.15
- Packagist: `typo3/cms-core` — affected >=13.0.0 <13.1.1

## Details
### Problem
The `ShowImageController` (_eID tx_cms_showpic_) lacks a cryptographic HMAC-signature on the `frame` HTTP query parameter (e.g. `/index.php?eID=tx_cms_showpic?file=3&...&frame=12345`).
This allows adversaries to instruct the system to produce an arbitrary number of thumbnail images on the server side.

### Solution
Update to TYPO3 versions 9.5.48 ELTS, 10.4.45 ELTS, 11.5.37 LTS, 12.4.15 LTS, 13.1.1 that fix the problem described.

#### ℹ️ **Strong security defaults - Manual actions required**

The `frame` HTTP query parameter is now ignored, since it could not be used by core APIs.

The new feature flag `security.frontend.allowInsecureFrameOptionInShowImageController` – which is disabled per default – can be used to reactivate the previous behavior.

### Credits
Thanks to TYPO3 security team member Torben Hansen who reported this issue and to TYPO3 core & security team members Benjamin Mack and Benjamin Franzke who fixed the issue.

### References
* [TYPO3-CORE-SA-2024-010](https://typo3.org/security/advisory/typo3-core-sa-2024-010)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-36g8-62qv-5957
- https://nvd.nist.gov/vuln/detail/CVE-2024-34358
- https://github.com/TYPO3/typo3/commit/05c95fed869a1a6dcca06c7077b83b6ea866ff14
- https://github.com/TYPO3/typo3/commit/1e70ebf736935413b0531004839362b4fb0755a5
- https://github.com/TYPO3/typo3/commit/df7909b6a1cf0f12a42994d0cc3376b607746142
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2024-010
