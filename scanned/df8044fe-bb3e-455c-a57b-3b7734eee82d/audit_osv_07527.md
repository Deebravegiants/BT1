# [H] SuiteCRM - Account Takeover in Password Reset Functionality

## Summary
Severity: High
Advisory: BIT-suitecrm-2021-25961
Aliases: CVE-2021-25961
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-suitecrm-2021-25961
Type: osv

## Affected
- Bitnami: `suitecrm` — affected >=7.11.0 <7.11.21

## Details
In “SuiteCRM” application, v7.1.7 through v7.10.31 and v7.11-beta through v7.11.20 fail to properly invalidate password reset links that is associated with a deleted user id, which makes it possible for account takeover of any newly created user with the same user id.

## References
- https://github.com/salesagility/SuiteCRM/commit/7124482fe07ee164923d974456ed31e45f65e513
- https://github.com/salesagility/SuiteCRM/commit/f463031bee59676d7d5be53bb32d551cd70a5648
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25961
- https://nvd.nist.gov/vuln/detail/CVE-2021-25961
