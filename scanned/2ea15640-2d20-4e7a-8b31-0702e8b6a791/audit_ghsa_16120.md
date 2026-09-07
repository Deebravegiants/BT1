# [M] loona-hpack Panic Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7vm6-qwh5-9x44
CVE: CVE-2024-51502
CWE: CWE-754, CWE-755
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-11-04
Source: https://github.com/advisories/GHSA-7vm6-qwh5-9x44
Type: github-advisory

## Affected
- crates.io: `loona-hpack` — affected >=0 <0.4.3

## Details
### Summary
`loona-hpack` suffers from the same vulnerability as the original `hpack` as documented in https://github.com/mlalic/hpack-rs/issues/11 

### Details
The original includes a very nice description of the problem, as well as an easy-enough fix for it.

### PoC
The original example pretty much still applies:
```rust
use loona_hpack::Decoder;

pub fn main() {
    let input = &[0x3f];
    let mut decoder = Decoder::new();
    let _ = decoder.decode(input);
}
```

### Impact
From the original:
`All users who try to decode untrusted input using the Decoder are vulnerable to this exploit. A patched version of the crate is available on [crates.io](https://crates.io/crates/hpack-patched) under the name hpack-patched. See [Cargo's documentation on overriding dependencies](https://doc.rust-lang.org/cargo/reference/overriding-dependencies.html) for more information.`

## References
- https://github.com/bearcove/loona/security/advisories/GHSA-7vm6-qwh5-9x44
- https://nvd.nist.gov/vuln/detail/CVE-2024-51502
- https://github.com/mlalic/hpack-rs/issues/11
- https://github.com/bearcove/loona/commit/9a4028ec6484f50a320281271a41a5040ddb1ba8
- https://github.com/advisories/GHSA-w7hm-hmxv-pvhf
- https://github.com/bearcove/loona
