# [H] Unbounded memory buffering in SelectorSocketTransport.writelines()

## Summary
Severity: High
Advisory: BIT-libpython-2024-12254
Aliases: BIT-python-2024-12254, BIT-python-min-2024-12254, CVE-2024-12254, PSF-2024-14
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2024-12254
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.13.0 <3.13.2

## Details
Starting in Python 3.12.0, the asyncio._SelectorSocketTransport.writelines()
 method would not "pause" writing and signal to the Protocol to drain 
the buffer to the wire once the write buffer reached the "high-water 
mark". Because of this, Protocols would not periodically drain the write
 buffer potentially leading to memory exhaustion.





This
 vulnerability likely impacts a small number of users, you must be using
 Python 3.12.0 or later, on macOS or Linux, using the asyncio module 
with protocols, and using .writelines() method which had new 
zero-copy-on-write behavior in Python 3.12.0 and later. If not all of 
these factors are true then your usage of Python is unaffected.

## References
- http://www.openwall.com/lists/oss-security/2024/12/06/1
- https://github.com/python/cpython/commit/71e8429ac8e2adc10084ab5ec29a62f4b6671a82
- https://github.com/python/cpython/commit/9aa0deb2eef2655a1029ba228527b152353135b5
- https://github.com/python/cpython/commit/e991ac8f2037d78140e417cc9a9486223eb3e786
- https://github.com/python/cpython/issues/127655
- https://github.com/python/cpython/pull/127656
- https://mail.python.org/archives/list/security-announce@python.org/thread/H4O3UBAOAQQXGT4RE3E4XQYR5XLROORB/
- https://nvd.nist.gov/vuln/detail/CVE-2024-12254
- https://security.netapp.com/advisory/ntap-20250404-0010/
