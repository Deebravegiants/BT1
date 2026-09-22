# [M] Password Shucking Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-c5vj-f36q-p9vg
CVE: CVE-2023-27580
CWE: CWE-916
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-03-13
Source: https://github.com/advisories/GHSA-c5vj-f36q-p9vg
Type: github-advisory

## Affected
- Packagist: `codeigniter4/shield` — affected >=0 <1.0.0-beta.4

## Details
### Impact
An improper implementation was found in the password storage process.

All hashed passwords stored in Shield v1.0.0-beta.3 or earlier are easier to crack than expected due to the vulnerability. Therefore, they should be removed as soon as possible.

If an attacker gets (1) the user's hashed password by Shield, and (2) the hashed password (SHA-384 hash without salt) from somewhere, the attacker may easily crack the user's password.

### Patches
Upgrade to Shield v1.0.0-beta.4 or later.

After upgrading, all users’ hashed passwords should be updated (saved to the database).
See https://github.com/codeigniter4/shield/blob/develop/UPGRADING.md for details.

### Workarounds
None.

### References
- https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html#pre-hashing-passwords
- https://blog.ircmaxell.com/2015/03/security-issue-combining-bcrypt-with.html
- https://www.scottbrady91.com/authentication/beware-of-password-shucking

### For more information
If you have any questions or comments about this advisory:
* Open an issue or discussion in [codeigniter4/shield](https://github.com/codeigniter4/shield)
* Email us at [security@codeigniter.com](mailto:security@codeigniter.com)

## References
- https://github.com/codeigniter4/shield/security/advisories/GHSA-c5vj-f36q-p9vg
- https://nvd.nist.gov/vuln/detail/CVE-2023-27580
- https://github.com/codeigniter4/shield/commit/ea9688dd01d100193d834117dbfc2cfabcf9ea0b
- https://blog.ircmaxell.com/2015/03/security-issue-combining-bcrypt-with.html
- https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html#pre-hashing-passwords
- https://github.com/codeigniter4/shield
- https://github.com/codeigniter4/shield/blob/develop/UPGRADING.md
- https://www.scottbrady91.com/authentication/beware-of-password-shucking
