# [H] Directus has MySQL accent insensitive email matching

## Summary
Severity: High
Advisory: GHSA-qw9g-7549-7wg5
CVE: CVE-2024-27295
CWE: CWE-706
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2024-03-01
Source: https://github.com/advisories/GHSA-qw9g-7549-7wg5
Type: github-advisory

## Affected
- npm: `directus` — affected >=0 <10.8.3

## Details
## Password reset vulnerable to accent confusion

The password reset mechanism of the Directus backend is implemented in a way where combined with (specific, need to double check if i can work around) configuration in MySQL or MariaDB. As such, it allows attackers to receive a password reset email of a victim user, specifically having it arrive at a similar email address as the victim with a one or more characters changed to use accents. 

This is due to the fact that by default MySQL/MariaDB are configured for accent-insenstive and case-insensitve comparisons.

MySQL weak comparison:
```sql
select 1 from directus_users where 'julian@cure53.de' = 'julian@cüre53.de';
```

This is exploitable due to an error in the API using the supplied email address for sending the reset password mail instead of using the email from the database.

### Steps to reproduce:

1. If the attacker knows the email address of the victim user, i.e., `julian@cure53.de`. (possibly just the domain could be enough for an educated guess)
2. A off-by-one accented domain `cüre53.de` can be registered to be able to receive emails.
3. With this email the attacker can request a password reset for `julian@cüre53.de`. 
```http
POST /auth/password/request HTTP/1.1
Host: example.com
[...]
{"email":"julian@cüre53.de"}
```
4. The supplied email (julian@cüre53.de) gets checked against the database and will match the non-accented email `julian@cure53.de` and will continue to email the password reset link to the provided email address instead of the saved email address.
5. With this email the attacker can log into the target account and use it for nefarious things

### Workarounds
Should be possible with collations but haven't been able to confirm this. 

### References
- https://www.monolune.com/articles/what-is-the-utf8mb4_0900_ai_ci-collation/
- https://dev.mysql.com/doc/refman/8.0/en/charset-unicode-sets.html

## References
- https://github.com/directus/directus/security/advisories/GHSA-qw9g-7549-7wg5
- https://nvd.nist.gov/vuln/detail/CVE-2024-27295
- https://github.com/directus/directus/commit/a8ef790ea2d28b1727f9027d99bd360920d57919
- https://dev.mysql.com/doc/refman/8.0/en/charset-unicode-sets.html
- https://github.com/directus/directus
- https://www.monolune.com/articles/what-is-the-utf8mb4_0900_ai_ci-collation
