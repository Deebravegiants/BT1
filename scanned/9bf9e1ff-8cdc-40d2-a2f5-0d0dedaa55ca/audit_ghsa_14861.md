# [C] Unable to generate the correct character set

## Summary
Severity: Critical
Advisory: GHSA-9hc7-6w9r-wj94
CVE: CVE-2024-36400
CWE: CWE-331
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2024-06-04
Source: https://github.com/advisories/GHSA-9hc7-6w9r-wj94
Type: github-advisory

## Affected
- crates.io: `nano-id` — affected >=0 <0.4.0

## Details
# Reduced entropy due to inadequate character set usage

## Description

Affected versions of the nano-id crate incorrectly generated IDs using a reduced character set in the `nano_id::base62` and `nano_id::base58` functions. Specifically, the `base62` function used a character set of 32 symbols instead of the intended 62 symbols, and the `base58` function used a character set of 16 symbols instead of the intended 58 symbols. Additionally, the `nano_id::gen` macro is also affected when a custom character set that is not a power of 2 in size is specified.

It should be noted that `nano_id::base64` is not affected by this vulnerability.

## Impact

This can result in a significant reduction in entropy, making the generated IDs predictable and vulnerable to brute-force attacks when the IDs are used in security-sensitive contexts such as session tokens or unique identifiers.

## Patches

The flaws were corrected in commit [a9022772b2f1ce38929b5b81eccc670ac9d3ab23](https://github.com/viz-rs/nano-id/commit/a9022772b2f1ce38929b5b81eccc670ac9d3ab23) by updating the the `nano_id::gen` macro to use all specified characters correctly.

## PoC

```rust
use std::collections::BTreeSet;

fn main() {
    test_base58();
    test_base62();
}

fn test_base58() {
    let mut produced_symbols = BTreeSet::new();

    for _ in 0..100_000 {
        let id = nano_id::base58::<10>();
        for c in id.chars() {
            produced_symbols.insert(c);
        }
    }

    println!(
        "{} symbols generated from nano_id::base58",
        produced_symbols.len()
    );
}

fn test_base62() {
    let mut produced_symbols = BTreeSet::new();

    for _ in 0..100_000 {
        let id = nano_id::base62::<10>();
        for c in id.chars() {
            produced_symbols.insert(c);
        }
    }

    println!(
        "{} symbols generated from nano_id::base62",
        produced_symbols.len()
    );
}
```

## References
- https://github.com/viz-rs/nano-id/security/advisories/GHSA-9hc7-6w9r-wj94
- https://nvd.nist.gov/vuln/detail/CVE-2024-36400
- https://github.com/viz-rs/nano-id/commit/a9022772b2f1ce38929b5b81eccc670ac9d3ab23
- https://github.com/viz-rs/nano-id
- https://rustsec.org/advisories/RUSTSEC-2024-0343.html
