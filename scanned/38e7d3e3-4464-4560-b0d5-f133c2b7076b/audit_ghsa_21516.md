# [M] Read the Docs vulnerable to Cross-Site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-98pf-gfh3-x3mp
CWE: CWE-79
Ecosystem: npm
Published: 2022-11-10
Source: https://github.com/advisories/GHSA-98pf-gfh3-x3mp
Type: github-advisory

## Affected
- npm: `readthedocs` — affected >=0 <8.8.1

## Details
### Impact

This vulnerability allowed a malicious user to serve arbitrary HTML files from the main application domain (readthedocs[.]org/readthedocs[.]com) by exploiting a vulnerability in the code that serves downloadable content from a project. 

Exploiting this would have required the attacker to get a logged-in user to visit the malicious URL, which would have allowed the attacker to take control of the user's session with JavaScript (making requests to the API/site on behalf of the user). This URL would have looked something like `hxxps[:]//readthedocs[.]org/projects/attacker-project/downloads/html/version-with-javascript-attack/`.

### Patches

This issue has been patched in our 8.8.1 release.

## References
- https://github.com/readthedocs/readthedocs.org/security/advisories/GHSA-98pf-gfh3-x3mp
- https://github.com/readthedocs/readthedocs.org/commit/b0ae626acd13882170ec5888e35f3ef2e48e6ff6
- https://github.com/readthedocs/readthedocs.org
