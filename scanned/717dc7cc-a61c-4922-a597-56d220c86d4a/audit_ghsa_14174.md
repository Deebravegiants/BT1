# [M] Cross-site Scripting (XSS) in Admin Login too many attempts notice

## Summary
Severity: Medium
Advisory: GHSA-fq95-rx4q-qgg2
CVE: CVE-2023-2341
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-04-27
Source: https://github.com/advisories/GHSA-fq95-rx4q-qgg2
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.21

## Details
### Impact
Malicious JavaScript has access to all the same objects as the rest of the web page, including access to cookies and local storage, which are often used to store session tokens. If an attacker can obtain a user's session cookie, they can then impersonate that user.

Furthermore, JavaScript can read and make arbitrary modifications to the contents of a page being displayed to a user. Therefore, XSS in conjunction with some clever social engineering opens up a lot of possibilities for an attacker.

### Patches
Update to version 10.5.21 or apply this patch manually https://github.com/pimcore/pimcore/commit/66f1089fb1b9bcd575bfce9b1d4abb0f0499df11.patch

### Workarounds
Apply patch https://github.com/pimcore/pimcore/commit/66f1089fb1b9bcd575bfce9b1d4abb0f0499df11.patch manually.

### References
https://huntr.dev/bounties/cf3901ac-a649-478f-ab08-094ef759c11d/

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-fq95-rx4q-qgg2
- https://nvd.nist.gov/vuln/detail/CVE-2023-2341
- https://github.com/pimcore/pimcore/commit/66f1089fb1b9bcd575bfce9b1d4abb0f0499df11
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/cf3901ac-a649-478f-ab08-094ef759c11d
