# [M] TYPO3-EXT-SA-2022-018: Multiple vulnerabilities in extension "Master-Quiz" (fp_masterquiz)

## Summary
Severity: Medium
Advisory: GHSA-7gpw-frph-fwrg
CVE: CVE-2022-47407
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-14
Source: https://github.com/advisories/GHSA-7gpw-frph-fwrg
Type: github-advisory

## Affected
- Packagist: `fixpunkt/fp-masterquiz` — affected >=3.0.0 <3.5.2
- Packagist: `fixpunkt/fp-masterquiz` — affected >=0 <2.2.1

## Details
An issue was discovered in the fp_masterquiz (aka Master-Quiz) extension before 2.2.1, and 3.x before 3.5.1, for TYPO3. An attacker can continue the quiz of a different user. In doing so, the attacker can view that user's answers and modify those answers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-47407
- https://github.com/bihor/fp_masterquiz/commit/f6f1baa594334c629637f5b87478ae31cdcaaa09
- https://github.com/bihor/fp_masterquiz/commit/fce4ec64600df3f38cacc9a86ba2bd063a51e140
- https://github.com/FriendsOfPHP/security-advisories/blob/master/fixpunkt/fp-masterquiz/CVE-2022-47407.yaml
- https://typo3.org/security/advisory/typo3-ext-sa-2022-018
