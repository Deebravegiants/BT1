# [H] HPACK decoder panics on invalid input

## Summary
Severity: High
Advisory: GHSA-w7hm-hmxv-pvhf
CWE: CWE-754
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-04-05
Source: https://github.com/advisories/GHSA-w7hm-hmxv-pvhf
Type: github-advisory

## Affected
- crates.io: `hpack` — affected >=0

## Details
Due to insufficient checking of input data, decoding certain data sequences can lead to _Decoder::decode_ panicking rather than returning an error.

Example code that triggers this vulnerability looks like this:

```rust
use hpack::Decoder;

pub fn main() {
  let input = &[0x3f];
  let mut decoder = Decoder::new();
  let _ = decoder.decode(input);
}
```

hpack is unmaintained. A crate with the panics fixed has been published as [hpack-patched](https://crates.io/crates/hpack-patched).

Also consider using [fluke-hpack](https://crates.io/crates/fluke-hpack) or [httlib-huffman](https://crates.io/crates/httlib-huffman) as an alternative.

## References
- https://github.com/mlalic/hpack-rs/issues/11
- https://github.com/sno2/hpack-rs-patched/commit/d669282924a95311599e9e7dd53869ee96b3a2f5
- https://github.com/mlalic/hpack-rs
- https://rustsec.org/advisories/RUSTSEC-2023-0085.html
