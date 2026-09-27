# [M] Paymenter doesn't reset email verification status after email change

## Summary
Severity: Medium
Advisory: GHSA-rv89-wch8-c574
CVE: CVE-2026-44584
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-rv89-wch8-c574
Type: github-advisory

## Affected
- Packagist: `paymenter/paymenter` — affected >=0 <1.5.0

## Details
### Summary
The email update functionality fails to invalidate the existing verification state when a user changes their email address, allowing a verified account to retain its verified status after switching to an unverified or unowned email address.

### Technical Details
When a user updated their email address, the system did not reset or revalidate the associated email verification status. As a result, the verification column remained set to “true” even after the email address was changed.

This allowed an attacker to:

- Verify an account using a legitimate email address
- Change the account email to an arbitrary or unowned address
- Retain the verified status without re-confirmation of the new email

No verification challenge or confirmation was required for the newly assigned email address.

### Impact
This vulnerability allows a user to associate a verified account with an email address they do not control, this may result in:

- Misrepresentation of email ownership
- Bypass of verification-based trust assumptions
- Potential abuse of features gated behind verified status

No direct unauthorized access to other users accounts or data is possible through this issue alone.

## References
- https://github.com/Paymenter/Paymenter/security/advisories/GHSA-rv89-wch8-c574
- https://github.com/Paymenter/Paymenter
