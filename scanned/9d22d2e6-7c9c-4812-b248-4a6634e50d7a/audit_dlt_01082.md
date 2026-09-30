# [M] stellar-strkey vulnerable to panic in SignedPayload::from_payload

## Summary
Severity: Medium
Chain: stellar-strkey
Component: stellar-strkey
CVE: CVE-2023-46135
CWE: Uncaught Exception
Published: 2023-10-25
Source: https://github.com/advisories/GHSA-5873-6fwq-463f
Type: github-advisory

## Details
### Impact
Panic vulnerability when a specially crafted payload is used. 
This is because of the following calculation:
```rust
inner_payload_len + (4 - inner_payload_len % 4) % 4
```
If `inner_payload_len` is `0xffffffff`, `(4 - inner_payload_len % 4) % 4 = 1` so
```rust
inner_payload_len + (4 - inner_payload_len % 4) % 4 = u32::MAX + 1
```
which overflow.

### Patches
Check that `inner_payload_len` is not above 64 which should never be the case.
Patched in version 0.0.8

### Workarounds
Sanitize input payload before it is passed to the vulnerable function so that bytes in `payload[32..32+4]` and parsed as a `u32` is not above 64.

### References
GitHub issue #58
