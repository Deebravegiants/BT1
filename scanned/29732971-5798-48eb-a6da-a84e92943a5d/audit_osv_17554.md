# [C] CVE-2020-16271

## Summary
Severity: Critical
Advisory: CVE-2020-16271
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2020-08-03
Source: https://osv.dev/vulnerability/CVE-2020-16271
Type: osv

## Details
The SRP-6a implementation in Kee Vault KeePassRPC before 1.12.0 generates insufficiently random numbers, which allows remote attackers to read and modify data in the KeePass database via a WebSocket connection.

## References
- https://forum.kee.pm/t/a-critical-security-update-for-keepassrpc-is-available/3040
- https://danzinger.wien/exploiting-keepassrpc/
