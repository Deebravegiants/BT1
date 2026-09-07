# [M] Shopware 6's password recovery link does not expire after email change

## Summary
Severity: Medium
Advisory: GHSA-2w46-vq8h-98vh
CWE: CWE-640
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2025-11-14
Source: https://github.com/advisories/GHSA-2w46-vq8h-98vh
Type: github-advisory

## Affected
- Packagist: `shopware/core` — affected >=0 <6.6.10.9
- Packagist: `shopware/core` — affected >=6.7.0.0 <6.7.4.1

## Details
### Summary
When a customer changes their email address after requesting a password reset, the old password reset link (tied to the previous email) remains valid. An attacker with access to the old email inbox is potentially able to reset the customer’s password even after the user changes their email address.

### PoC

1. Log in to a Shopware account.
2. Request a password reset for your current email address.
3. Copy the password reset link but do not open it.
4. Log back into your account.n
5. Navigate to Account Settings → Email and change your email address.
6. Use the previously copied reset link (from before the email change).
7. The system allows password change using the old link.

### Impact
Reproduced on Stable 6.6.10.7 and trunk.

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-2w46-vq8h-98vh
- https://github.com/shopware/shopware/commit/1338dd9a11e361639704bf8f09b6878552eb8c13
- https://github.com/shopware/shopware/commit/2fb94855696a90045b81c503d216ba7df8e64e52
- https://github.com/shopware/shopware
- https://github.com/shopware/shopware/releases/tag/v6.6.10.9
- https://github.com/shopware/shopware/releases/tag/v6.7.0.0
- https://github.com/shopware/shopware/releases/tag/v6.7.4.1
