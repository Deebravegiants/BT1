# [M] POP3 command injection in user-controlled commands

## Summary
Severity: Medium
Advisory: BIT-libpython-2025-15367
Aliases: BIT-python-2025-15367, BIT-python-min-2025-15367, CVE-2025-15367, PSF-2026-4
Ecosystem: Bitnami
Published: 2026-01-26
Source: https://osv.dev/vulnerability/BIT-libpython-2025-15367
Type: osv

## Affected
- Bitnami: `libpython` — affected >=0 <3.15.0

## Details
The poplib module, when passed a user-controlled command, can have
additional commands injected using newlines. Mitigation rejects commands
containing control characters.

## References
- https://github.com/python/cpython/commit/b234a2b67539f787e191d2ef19a7cbdce32874e7
- https://github.com/python/cpython/issues/143923
- https://github.com/python/cpython/pull/143924
- https://mail.python.org/archives/list/security-announce@python.org/thread/CBFBOWVGGUJFSGITQCCBZS4GEYYZ7ZNE/
- https://nvd.nist.gov/vuln/detail/CVE-2025-15367
