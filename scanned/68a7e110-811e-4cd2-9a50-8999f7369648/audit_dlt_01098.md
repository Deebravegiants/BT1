# [H] Unexpected panic in multihash

## Summary
Severity: High
Chain: multihash
Component: multihash
CVE: CVE-2020-35909
CWE: Improper Input Validation
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-h7qh-3h6f-w79p
Type: github-advisory

## Details
In versions prior 0.11.3 it's possible to make from_slice panic by feeding it certain malformed input. It's never documented that from_slice (and from_bytes which wraps it) can panic, and its' return type (Result<Self, DecodeError>) suggests otherwise. In practice, from_slice/from_bytes is frequently used in networking code and is being called with unsanitized data from untrusted sources. This can allow attackers to cause DoS by causing an unexpected panic in the network client's code..
