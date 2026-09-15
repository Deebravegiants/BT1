# [H] CVE-2022-46303

## Summary
Severity: High
Advisory: CVE-2022-46303
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-02-20
Source: https://osv.dev/vulnerability/CVE-2022-46303
Type: osv

## Details
Command injection in SMS notifications in Tribe29 Checkmk <= 2.1.0p10, Checkmk <= 2.0.0p27, and Checkmk <= 1.6.0p29 allows an attacker with User Management permissions, as well as LDAP administrators in certain scenarios, to perform arbitrary commands within the context of the application's local permissions.

## References
- https://checkmk.com/werk/14381
