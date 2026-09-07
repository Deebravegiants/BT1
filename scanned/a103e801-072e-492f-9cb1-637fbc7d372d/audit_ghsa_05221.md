# [H] MessagePack for Python: Out-of-bounds read / crash on Unpacker reuse after a caught error

## Summary
Severity: High
Advisory: GHSA-6v7p-g79w-8964
CWE: CWE-416
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-6v7p-g79w-8964
Type: github-advisory

## Affected
- PyPI: `msgpack` — affected >=0 <1.2.1

## Details
### Impact

If the Unpacker is used repeatedly after an error occurs, the process may crash with a SEGV.

If the Unpacker is used repeatedly to unpack untrusted input from external sources, it may be vulnerable to a DoS attack.

### Patches

v1.2.1

### Workarounds

Users should create a new Unpacker instead of reusing the same Unpacker after an error occurs.

Applying the above patch can prevent SEGV, but reusing the Streaming Unpacker after it has encountered an error will not yield correct data. If an error occurs during Streaming Unpacking, the Stream and Streaming Unpacker should be discarded.

Therefore, this is not just a workaround but the correct solution. The above patch only prevents crashes from incorrect usage.

## References
- https://github.com/msgpack/msgpack-python/security/advisories/GHSA-6v7p-g79w-8964
- https://github.com/msgpack/msgpack-python/commit/2c56ddb5d0025ed481d962c0f5d62d19dec7476d
- https://github.com/msgpack/msgpack-python
- https://github.com/msgpack/msgpack-python/releases/tag/v1.2.1
