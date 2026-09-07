# [M] TokenController formName not sanitized in hidden input

## Summary
Severity: Medium
Advisory: GHSA-rrvc-c7xg-7cf3
CVE: CVE-2024-37156
CWE: CWE-79, CWE-80
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-06
Source: https://github.com/advisories/GHSA-rrvc-c7xg-7cf3
Type: github-advisory

## Affected
- Packagist: `sulu/form-bundle` — affected >=2.0.0 <2.5.3

## Details
### Impact

TokenController get parameter formName not sanitized in returned input field leads to XSS.

_What kind of vulnerability is it? Who is impacted?_

### Patches

_Has the problem been patched? What versions should users upgrade to?_

### Workarounds

_Is there a way for users to fix or remediate the vulnerability without upgrading?_

Create a custom Symfony Request listener which checks for the get value of `form` for the TokenController and if not valid stop the request dispatching and return a error status code.

### References

_Are there any links users can visit to find out more?_

## References
- https://github.com/sulu/SuluFormBundle/security/advisories/GHSA-rrvc-c7xg-7cf3
- https://nvd.nist.gov/vuln/detail/CVE-2024-37156
- https://github.com/sulu/SuluFormBundle/commit/3f341b71a7309cbc8fd2c5bff894c654d1679b17
- https://github.com/sulu/SuluFormBundle
