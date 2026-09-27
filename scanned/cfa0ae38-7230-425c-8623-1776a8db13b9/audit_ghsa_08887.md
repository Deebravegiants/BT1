# [H] eduMFA: Incorrect InnoDB snapshot isolation possibly allows token reusage

## Summary
Severity: High
Advisory: GHSA-qq2p-4282-cfc5
CWE: CWE-285
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:P/VC:H/VI:L/VA:L/SC:H/SI:L/SA:L (CVSS_V4)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-qq2p-4282-cfc5
Type: github-advisory

## Affected
- PyPI: `edumfa` — affected >=0 <2.9.1

## Details
### Impact

For deployments using MySQL or MariaDB < 11.6.2 (or newer with innodb_snapshot_isolation=off) reusage of token values might be possible due to faulty transaction isolation inside the database. Exploiting this requires racing this transaction.
Affected are all tokentypes whose values are only supposed to be used once, for example TOTP, HOTP and likely also WebAuthN.

#### Affected Combinations:

- MySQL (any version)
- MariaDB with innodb_snapshot_isolation=OFF
  - innodb_snapshot_isolation was introduced in: MariaDB 10.6.18, MariaDB 10.11.8, MariaDB 11.0.6, MariaDB 11.1.5, MariaDB 11.2.4, MariaDB 11.4.2
    with default OFF, can be turned ON as a workaround
  - for MariaDB >= 11.6.2 the default is ON, which is not affected
- Same rules applies for Galera with underlying MariaDB

### Patches
Fixed in version 2.9.1 by locking rows prior to write with SELECT FOR UPDATE.

### Workarounds
Set innodb_snapshot_isolation to ON (default in MariaDB >= 11.6.2, e.g packaged in Debian 13).

### Resources
https://mariadb.com/resources/blog/isolation-level-violation-testing-and-debugging-in-mariadb/

## References
- https://github.com/eduMFA/eduMFA/security/advisories/GHSA-qq2p-4282-cfc5
- https://github.com/eduMFA/eduMFA
