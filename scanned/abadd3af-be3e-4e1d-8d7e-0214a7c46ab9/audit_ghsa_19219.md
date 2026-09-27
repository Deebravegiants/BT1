# [M] Mautic allows user name enumeration due to response time difference on password reset form

## Summary
Severity: Medium
Advisory: GHSA-424x-cxvh-wq9p
CVE: CVE-2024-47057
CWE: CWE-203, CWE-204
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-05-28
Source: https://github.com/advisories/GHSA-424x-cxvh-wq9p
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=1.0.0 <4.4.16
- Packagist: `mautic/core` — affected >=5.0.0-alpha <5.2.6
- Packagist: `mautic/core` — affected >=6.0.0-alpha <6.0.2

## Details
### Summary

This advisory addresses a security vulnerability in Mautic related to the "Forget your password" functionality. This vulnerability could be exploited by unauthenticated users to enumerate valid usernames.

User Enumeration via Timing Attack: A user enumeration vulnerability exists in the "Forget your password" functionality. Differences in response times for existing and non-existing users, combined with a lack of request limiting, allow an attacker to determine the existence of usernames through a timing-based attack.

### Mitigation
Please update to a version that addresses this timing vulnerability, where password reset responses are normalized to respond at the same time regardless of user existence.

### Workarounds
None

If you have any questions or comments about this advisory:
Email us at security@mautic.org

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-424x-cxvh-wq9p
- https://nvd.nist.gov/vuln/detail/CVE-2024-47057
- https://github.com/mautic/mautic
