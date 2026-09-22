# [H] protobuf affected by a JSON recursion depth bypass

## Summary
Severity: High
Advisory: GHSA-7gcm-g887-7qv7
CVE: CVE-2026-0994
CWE: CWE-674
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:L (CVSS_V4)
Published: 2026-01-23
Source: https://github.com/advisories/GHSA-7gcm-g887-7qv7
Type: github-advisory

## Affected
- PyPI: `protobuf` — affected >=6.30.0rc1 <6.33.5
- PyPI: `protobuf` — affected >=0 <5.29.6

## Details
A denial-of-service (DoS) vulnerability exists in google.protobuf.json_format.ParseDict() in Python, where the max_recursion_depth limit can be bypassed when parsing nested google.protobuf.Any messages.

Due to missing recursion depth accounting inside the internal Any-handling logic, an attacker can supply deeply nested Any structures that bypass the intended recursion limit, eventually exhausting Python’s recursion stack and causing a RecursionError.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-0994
- https://github.com/protocolbuffers/protobuf/issues/25070
- https://github.com/protocolbuffers/protobuf/pull/25239
- https://github.com/protocolbuffers/protobuf/commit/5ebddcb1bcbe51d1fe323baa145e85f4f23128cf
- https://github.com/protocolbuffers/protobuf/commit/d2b001626d137c62dfee6c88c87324102531868b
- https://github.com/protocolbuffers/protobuf
