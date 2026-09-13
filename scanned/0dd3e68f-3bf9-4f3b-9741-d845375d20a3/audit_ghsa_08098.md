# [C] Statamic is vulnerable to account takeover via password reset link injection

## Summary
Severity: Critical
Advisory: GHSA-jxq9-79vj-rgvw
CVE: CVE-2026-27593
CWE: CWE-640
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-jxq9-79vj-rgvw
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=0 <5.73.10
- Packagist: `statamic/cms` — affected >=6.0.0-alpha.1 <6.7.1

## Details
## Impact

An attacker may leverage a vulnerability in the password reset feature to capture a user's token and reset the password on their behalf.

The attacker must know the email address of a valid account on the site, and the actual user must blindly click the link in their email even though they didn't request the reset.

## Patches

This has been fixed in 6.7.1 and 5.73.10.

Note that a follow-up report showed the original 6.3.3 fix to be insufficient. The 5.73.10 fix was sufficient.

## References
- https://github.com/statamic/cms/security/advisories/GHSA-jxq9-79vj-rgvw
- https://nvd.nist.gov/vuln/detail/CVE-2026-27593
- https://github.com/statamic/cms/commit/6fdd03324982848e8754f2edd2265262d361714e
- https://github.com/statamic/cms/commit/78e63dfcf705b116d5ac0f7f7f5a1a69be63d1be
- https://github.com/statamic/cms/commit/b2be592ddfb588bcb88c9be454f3590e14b145b0
- https://github.com/statamic/cms
- https://github.com/statamic/cms/releases/tag/v5.73.10
- https://github.com/statamic/cms/releases/tag/v6.3.3
