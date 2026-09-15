# [M] Mautic Vulnerable to User Enumeration via Response Timing

## Summary
Severity: Medium
Advisory: GHSA-3ggv-qwcp-j6xg
CVE: CVE-2025-9824
CWE: CWE-204
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-09-03
Source: https://github.com/advisories/GHSA-3ggv-qwcp-j6xg
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=4.4.0 <4.4.17
- Packagist: `mautic/core` — affected >=5.0.0-alpha <5.2.8
- Packagist: `mautic/core` — affected >=6.0.0-alpha <6.0.5

## Details
### Impact
The attacker can validate if a user exists by checking the time login returns. This timing difference can be used to enumerate valid usernames, after which an attacker could attempt brute force attacks.

### Patches
This vulnerability has been patched, implementing a timing-safe form login authenticator that ensures consistent response times regardless of whether a user exists or not.

### Technical Details
The vulnerability was caused by different response times when:
- A valid username was provided (password hashing occurred)
- An invalid username was provided (no password hashing occurred)

The fix introduces a `TimingSafeFormLoginAuthenticator` that performs a dummy password hash verification even for non-existent users, ensuring consistent timing.

### Workarounds
No workarounds are available. Users should upgrade to the patched version.

### References
- https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/03-Identity_Management_Testing/04-Testing_for_Account_Enumeration_and_Guessable_User_Account
- https://github.com/mautic/mautic-security/pull/146

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-3ggv-qwcp-j6xg
- https://nvd.nist.gov/vuln/detail/CVE-2025-9824
- https://github.com/mautic/mautic/commit/6bc4f5f1aabb13df12714ad0ea9fc281cbb867c6
- https://github.com/mautic/mautic/commit/b4264c717ce31fbafafcefc04b02ecb9fb911e62
- https://github.com/mautic/mautic
