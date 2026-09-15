# [M] Disclosure of unrelated data in libmemcached-awesome

## Summary
Severity: Medium
Advisory: BIT-libmemcached-2023-27478
Aliases: BIT-memcached-2023-27478, CVE-2023-27478, GHSA-wwmh-39wj-fx59
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-libmemcached-2023-27478
Type: osv

## Affected
- Bitnami: `libmemcached` — affected >=1.0.18 <1.1.4

## Details
libmemcached-awesome is an open source C/C++ client library and tools for the memcached server. `libmemcached` could return data for a previously requested key, if that previous request timed out due to a low `POLL_TIMEOUT`. This issue has been addressed in version 1.1.4. Users are advised to upgrade. There are several ways to workaround or lower the probability of this bug affecting a given deployment. 1: use a reasonably high `POLL_TIMEOUT` setting, like the default. 2: use separate libmemcached connections for unrelated data. 3: do not re-use libmemcached connections in an unknown state.

## References
- https://github.com/awesomized/libmemcached/commit/48dcc61a
- https://github.com/awesomized/libmemcached/releases/tag/1.1.4
- https://github.com/awesomized/libmemcached/security/advisories/GHSA-wwmh-39wj-fx59
- https://github.com/php-memcached-dev/php-memcached/issues/531
- https://nvd.nist.gov/vuln/detail/CVE-2023-27478
