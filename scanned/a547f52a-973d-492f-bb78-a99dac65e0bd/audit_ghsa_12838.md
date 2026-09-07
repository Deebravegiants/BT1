# [M] a12nserver vulnerable to potential SQL Injections via Knex dependency

## Summary
Severity: Medium
Advisory: GHSA-crhg-xgrg-vvcc
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-01-13
Source: https://github.com/advisories/GHSA-crhg-xgrg-vvcc
Type: github-advisory

## Affected
- npm: `@curveball/a12n-server` — affected >=0.20.0 <0.23.0

## Details
### Impact

Users of a12nserver that use MySQL might be vulnerable to SQL injection bugs. 

If you use a12nserver and MySQL, update as soon as possible. This SQL injection bug might let an attacker obtain OAuth2 Access Tokens for users unrelated to those that permitted OAuth2 clients.

### Patches

The knex dependency has been updated to 2.4.0 in a12nserver 0.23.0

### Workarounds

No further workarounds

### References

* https://github.com/knex/knex/issues/1227
* https://nvd.nist.gov/vuln/detail/CVE-2016-20018
* https://www.ghostccamm.com/blog/knex_sqli/

## References
- https://github.com/curveball/a12n-server/security/advisories/GHSA-crhg-xgrg-vvcc
- https://nvd.nist.gov/vuln/detail/CVE-2016-20018
- https://github.com/knex/knex/issues/1227
- https://github.com/curveball/a12n-server/commit/f4acd7549043e6e2b8917b77a50dce0756a922cc
- https://github.com/curveball/a12n-server
- https://github.com/curveball/a12n-server/releases/tag/v0.23.0
- https://www.ghostccamm.com/blog/knex_sqli
