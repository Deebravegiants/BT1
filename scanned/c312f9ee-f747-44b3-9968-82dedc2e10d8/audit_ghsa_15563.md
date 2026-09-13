# [M] Mautic allows users enumeration due to weak password login

## Summary
Severity: Medium
Advisory: GHSA-8vff-35qm-qjvv
CVE: CVE-2024-47059
CWE: CWE-200, CWE-204
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-09-18
Source: https://github.com/advisories/GHSA-8vff-35qm-qjvv
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=5.1.0 <5.1.1

## Details
### Summary

When logging in with the correct username and incorrect weak password, the user receives the notification, that their password is too weak.

However when an incorrect username is provided along side with weak password, the application responds with ’Invalid credentials’ notification.

This difference could be used to perform username enumeration.

### Patches

Update to 5.1.1 or later.

If you have any questions or comments about this advisory:

Email us at [security@mautic.org](mailto:security@mautic.org)

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-8vff-35qm-qjvv
- https://nvd.nist.gov/vuln/detail/CVE-2024-47059
- https://github.com/mautic/mautic
