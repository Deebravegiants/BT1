# [M] Quadratic complexity in os.path.expandvars() with user-controlled template

## Summary
Severity: Medium
Advisory: BIT-libpython-2025-6075
Aliases: BIT-python-2025-6075, BIT-python-min-2025-6075, CVE-2025-6075, PSF-2025-13
Ecosystem: Bitnami
Published: 2025-12-05
Source: https://osv.dev/vulnerability/BIT-libpython-2025-6075
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.14.0 <3.14.1

## Details
If the value passed to os.path.expandvars() is user-controlled a 
performance degradation is possible when expanding environment 
variables.

## References
- https://github.com/python/cpython/commit/2e6150adccaaf5bd95d4c19dfd04a36e0b325d8c
- https://github.com/python/cpython/commit/5dceb93486176e6b4a6d9754491005113eb23427
- https://github.com/python/cpython/commit/631ba3407e3348ccd56ce5160c4fb2c5dc5f4d84
- https://github.com/python/cpython/commit/892747b4cf0f95ba8beb51c0d0658bfaa381ebca
- https://github.com/python/cpython/commit/9ab89c026aa9611c4b0b67c288b8303a480fe742
- https://github.com/python/cpython/commit/c8a5f3435c342964e0a432cc9fb448b7dbecd1ba
- https://github.com/python/cpython/commit/f029e8db626ddc6e3a3beea4eff511a71aaceb5c
- https://github.com/python/cpython/issues/136065
- https://mail.python.org/archives/list/security-announce@python.org/thread/IUP5QJ6D4KK6ULHOMPC7DPNKRYQTQNLA/
- https://nvd.nist.gov/vuln/detail/CVE-2025-6075
