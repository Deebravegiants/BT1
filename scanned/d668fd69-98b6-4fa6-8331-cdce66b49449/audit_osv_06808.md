# [H] BIT-memcached-2026-47783

## Summary
Severity: High
Advisory: BIT-memcached-2026-47783
Aliases: CVE-2026-47783
Ecosystem: Bitnami
Published: 2026-05-22
Source: https://osv.dev/vulnerability/BIT-memcached-2026-47783
Type: osv

## Affected
- Bitnami: `memcached` — affected >=0 <1.6.42

## Details
In memcached before 1.6.42, username data for SASL password database authentication has a timing side channel because a loop exits as soon as a valid username is found by sasl_server_userdb_checkpass.

## References
- https://github.com/memcached/memcached/commit/d13f282b4bce33a9c33b8a1bbf07f12114160fed
- https://github.com/memcached/memcached/compare/1.6.41...1.6.42
- https://github.com/memcached/memcached/wiki/ReleaseNotes1642
- https://nvd.nist.gov/vuln/detail/CVE-2026-47783
- https://access.redhat.com/errata/RHSA-2026:27842
- https://access.redhat.com/errata/RHSA-2026:27862
- https://access.redhat.com/security/cve/CVE-2026-47783
- https://bugzilla.redhat.com/show_bug.cgi?id=2480089
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-47783.json
