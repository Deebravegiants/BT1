# [M] Tribal Systems Zenario CMS vulnerable to Session Fixation

## Summary
Severity: Medium
Advisory: GHSA-6657-9743-4mc6
CVE: CVE-2022-4231
CWE: CWE-384
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-11-30
Source: https://github.com/advisories/GHSA-6657-9743-4mc6
Type: github-advisory

## Affected
- Packagist: `tribalsystems/zenario` — affected >=0

## Details
Tribal Systems Zenario CMS 9.3.57595 is vulnerable to session fixation. In Zenario CMS, the user session identifier (authentication token) is issued to the browser prior to authentication but is not changed after user logout and login again into the application when "Remember me" option active. Failing to issue a new session ID following a successful login introduces the possibility for an attacker to set up a trap session on the device the victim is likely to login with. The attack may be initiated remotely and an exploit has been disclosed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4231
- https://github.com/TribalSystems/Zenario
- https://github.com/lithonn/bug-report/tree/main/vendors/tribalsystems/zenario/session-fixation
- https://vuldb.com/?id.214589
