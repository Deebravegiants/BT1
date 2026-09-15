# [H] Navidrome Stores JWT Secret in Plaintext in navidrome.db

## Summary
Severity: High
Advisory: GHSA-xwx7-p63r-2rj8
CVE: CVE-2024-56362
CWE: CWE-312
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-12-23
Source: https://github.com/advisories/GHSA-xwx7-p63r-2rj8
Type: github-advisory

## Affected
- Go: `github.com/navidrome/navidrome` — affected >=0 <0.54.1

## Details
Navidrome stores the JWT secret in plaintext in the `navidrome.db` database file under the `property` table. This practice introduces a security risk because anyone with access to the database file can retrieve the secret.
The JWT secret is critical for the authentication and authorization system. If exposed, an attacker could:
- Forge valid tokens to impersonate users, including administrative accounts.
- Gain unauthorized access to sensitive data or perform privileged actions.
This vulnerability has been tested on the latest version of Navidrome and poses a significant risk in environments where the database file is not adequately secured.

![image](https://github.com/user-attachments/assets/29aae867-f21f-4d70-bda0-d2bb87d754d9)

## References
- https://github.com/navidrome/navidrome/security/advisories/GHSA-xwx7-p63r-2rj8
- https://nvd.nist.gov/vuln/detail/CVE-2024-56362
- https://github.com/navidrome/navidrome/commit/7f030b0859653593fd2ac0df69f4a313f9caf9ff
- https://github.com/navidrome/navidrome/commit/9cbdb20a318a49daf95888b1fd207d4d729b55f1
- https://github.com/navidrome/navidrome
- https://github.com/navidrome/navidrome/releases/tag/v0.54.1
- https://pkg.go.dev/vuln/GO-2024-3357
