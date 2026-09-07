# [H] MantisBT vulnerable to authentication bypass for some passwords due to PHP type juggling

## Summary
Severity: High
Advisory: GHSA-4v8w-gg5j-ph37
CVE: CVE-2025-47776
CWE: CWE-305, CWE-697
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-11-03
Source: https://github.com/advisories/GHSA-4v8w-gg5j-ph37
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.27.2

## Details
Due to an incorrect use of loose (`==`) instead of strict (`===`) comparison in the [authentication code][1], PHP type juggling will cause interpretation of certain MD5 hashes as numbers, specifically those matching scientific notation.

[1]: https://github.com/mantisbt/mantisbt/blob/0fb502dd613991e892ed2224ac5ea3e40ba632bc/core/authentication_api.php#L782

### Impact
On MantisBT instances configured to use the *MD5* login method, user accounts having a password hash evaluating to zero (i.e. matching regex `^0+[Ee][0-9]+$`) are vulnerable, allowing an attacker knowing the victim's username to login without knowledge of their actual password, using any other password having a  hash evaluating to zero, for example `comito5` (0e579603064547166083907005281618). 

No password bruteforcing for individual users is needed, thus $g_max_failed_login_count does not protect against the attack.

### Patches
* https://github.com/mantisbt/mantisbt/commit/966554a19cf1bdbcfbfb3004766979faa748f9a2

### Workarounds
Check the database for vulnerable accounts, and change those users' passwords, e.g. for MySQL:
```sql
SELECT username, email FROM mantis_user_table WHERE password REGEXP '^0+[Ee][0-9]+$'
```

### References
- https://mantisbt.org/bugs/view.php?id=35967

### Credits
Thanks to Harry Sintonen / Reversec for discovering and reporting the issue.

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-4v8w-gg5j-ph37
- https://nvd.nist.gov/vuln/detail/CVE-2025-47776
- https://github.com/mantisbt/mantisbt/commit/966554a19cf1bdbcfbfb3004766979faa748f9a2
- https://github.com/mantisbt/mantisbt
- https://github.com/mantisbt/mantisbt/blob/0fb502dd613991e892ed2224ac5ea3e40ba632bc/core/authentication_api.php#L782
- https://mantisbt.org/bugs/view.php?id=35967
