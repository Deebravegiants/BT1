# [H] Use after free in C++ protobuf

## Summary
Severity: High
Advisory: CVE-2024-2410
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L)
Published: 2024-05-03
Source: https://osv.dev/vulnerability/CVE-2024-2410
Type: osv

## Details
The JsonToBinaryStream() function is part of the protocol buffers C++ implementation and is used to parse JSON from a stream. If the input is broken up into separate chunks in a certain way, the parser will attempt to read bytes from a chunk that has already been freed.

## References
- https://github.com/protocolbuffers/protobuf/releases/tag/v25.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/2xxx/CVE-2024-2410.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-2410
- https://github.com/protocolbuffers/protobuf
