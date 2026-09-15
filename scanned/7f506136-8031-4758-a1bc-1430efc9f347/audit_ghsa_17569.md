# [H] protobuf-python has a potential Denial of Service issue

## Summary
Severity: High
Advisory: GHSA-8qvm-5x2c-j2w7
CVE: CVE-2025-4565
CWE: CWE-674
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-06-16
Source: https://github.com/advisories/GHSA-8qvm-5x2c-j2w7
Type: github-advisory

## Affected
- PyPI: `protobuf` — affected >=0 <4.25.8
- PyPI: `protobuf` — affected >=5.26.0rc1 <5.29.5
- PyPI: `protobuf` — affected >=6.30.0rc1 <6.31.1

## Details
### Summary
Any project that uses Protobuf pure-Python backend to parse untrusted Protocol Buffers data containing an arbitrary number of **recursive groups**, **recursive messages** or **a series of [`SGROUP`](https://protobuf.dev/programming-guides/encoding/#groups) tags** can be corrupted by exceeding the Python recursion limit.

Reporter: Alexis Challande, Trail of Bits Ecosystem Security Team
[ecosystem@trailofbits.com](mailto:ecosystem@trailofbits.com)

Affected versions: This issue only affects the [pure-Python implementation](https://github.com/protocolbuffers/protobuf/tree/main/python#implementation-backends) of protobuf-python backend. This is the implementation when `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python` environment variable is set or the default when protobuf is used from Bazel or pure-Python PyPi wheels. CPython PyPi wheels do not use pure-Python by default.

This is a Python variant of a [previous issue affecting protobuf-java](https://github.com/protocolbuffers/protobuf/security/advisories/GHSA-735f-pc8j-v9w8).

### Severity
This is a potential Denial of Service. Parsing nested protobuf data creates unbounded recursions that can be abused by an attacker.

### Proof of Concept
For reproduction details, please refer to the unit tests [decoder_test.py](https://github.com/protocolbuffers/protobuf/blob/main/python/google/protobuf/internal/decoder_test.py#L87-L98) and [message_test](https://github.com/protocolbuffers/protobuf/blob/main/python/google/protobuf/internal/message_test.py#L1436-L1478)

### Remediation and Mitigation
A mitigation is available now. Please update to the latest available versions of the following packages:
* protobuf-python(4.25.8, 5.29.5, 6.31.1)

## References
- https://github.com/protocolbuffers/protobuf/security/advisories/GHSA-735f-pc8j-v9w8
- https://github.com/protocolbuffers/protobuf/security/advisories/GHSA-8qvm-5x2c-j2w7
- https://nvd.nist.gov/vuln/detail/CVE-2025-4565
- https://github.com/protocolbuffers/protobuf/commit/17838beda2943d08b8a9d4df5b68f5f04f26d901
- https://github.com/protocolbuffers/protobuf
- https://github.com/protocolbuffers/protobuf/blob/main/python/google/protobuf/internal/decoder_test.py#L87-L98
- https://github.com/protocolbuffers/protobuf/blob/main/python/google/protobuf/internal/message_test.py#L1436-L1478
- https://github.com/protocolbuffers/protobuf/tree/main/python#implementation-backends
