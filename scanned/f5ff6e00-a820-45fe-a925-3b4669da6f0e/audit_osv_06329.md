# [M] IMAP command injection in user-controlled commands

## Summary
Severity: Medium
Advisory: BIT-libpython-2025-15366
Aliases: BIT-python-2025-15366, BIT-python-min-2025-15366, CVE-2025-15366, PSF-2026-3
Ecosystem: Bitnami
Published: 2026-01-26
Source: https://osv.dev/vulnerability/BIT-libpython-2025-15366
Type: osv

## Affected
- Bitnami: `libpython` — affected >=0 <3.15.0

## Details
The imaplib module, when passed a user-controlled command, can have additional commands injected using newlines. Mitigation rejects commands containing control characters.

## References
- https://github.com/python/cpython/commit/6262704b134db2a4ba12e85ecfbd968534f28b45
- https://github.com/python/cpython/issues/143921
- https://github.com/python/cpython/pull/143922
- https://mail.python.org/archives/list/security-announce@python.org/thread/DD7C7JZJYTBXMDOWKCEIEBJLBRU64OMR/
- https://nvd.nist.gov/vuln/detail/CVE-2025-15366
