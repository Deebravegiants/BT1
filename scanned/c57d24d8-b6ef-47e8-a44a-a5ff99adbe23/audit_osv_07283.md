# [M] BIT-phplist-2023-27576

## Summary
Severity: Medium
Advisory: BIT-phplist-2023-27576
Aliases: CVE-2023-27576
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-phplist-2023-27576
Type: osv

## Affected
- Bitnami: `phplist` — affected >=3.6.12

## Details
An issue was discovered in phpList before 3.6.14. Due to an access error, it was possible to manipulate and edit data of the system's super admin, allowing one to perform an account takeover of the user with super-admin permission. Specifically, for a request with updatepassword=1, a modified request (manipulating both the ID parameter and the associated username) can bypass the intended email confirmation requirement. For example, the attacker can start from an updatepassword=1 request with their own ID number, and change the ID number to 1 (representing the super admin account) and change the username to admin2. In the first step, the attacker changes the super admin's email address to one under the attacker's control. In the second step, the attacker performs a password reset for the super admin account. The new password allows login as the super admin, i.e., a successful account takeover.

## References
- https://cupc4k3.lol/cve-2023-27576-hacking-phplist-how-i-gained-super-admin-access-44c7c90d82da
- https://github.com/phpList/phplist3/pull/986
- https://www.phplist.org/newslist/phplist-3-6-14-release-notes/
