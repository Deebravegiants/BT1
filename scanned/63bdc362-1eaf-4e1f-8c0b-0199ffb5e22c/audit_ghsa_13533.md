# [M] Sequential calls of encryption API (`encrypt`, `wrap`, and `dump`) result in nonce reuse

## Summary
Severity: Medium
Advisory: GHSA-6878-6wc2-pf5h
CVE: CVE-2024-21530
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-10-24
Source: https://github.com/advisories/GHSA-6878-6wc2-pf5h
Type: github-advisory

## Affected
- crates.io: `cocoon` — affected >=0 <0.4.0

## Details
**Problem**: Trying to create a new encrypted message with the same cocoon object generates the same ciphertext. It mostly affects `MiniCocoon` and `Cocoon` objects with custom seeds and RNGs (where `StdRng` is used under the hood).

**Note**: The issue does **NOT** affect objects created with **`Cocoon::new`** which utilizes `ThreadRng`.

**Cause**: `StdRng` produces the same nonce because `StdRng::clone` resets its state.

**Measure**: Make encryption API mutable (`encrypt`, `wrap`, and `dump`).

**Workaround**: Create a new cocoon object with a new **seed** per each encryption.

## How to Reproduce

```rust
let cocoon = MiniCocoon::from_password(b"password", &[1; 32]);
let mut data1 = "my secret data".to_owned().into_bytes();
let _ = cocoon.encrypt(&mut data1)?;

let mut data2 = "my secret data".to_owned().into_bytes();
let _ = cocoon.encrypt(&mut data2)?;

// data1: [23, 217, 251, 151, 179, 62, 85, 15, 253, 92, 192, 112, 200, 52]
// data2: [23, 217, 251, 151, 179, 62, 85, 15, 253, 92, 192, 112, 200, 52]
```

## Workaround

For `cocoon <= 0.3.3`, create a new cocoon with a different **seed** per each `encrypt`/`wrap`/`dump` call.

```rust
let cocoon = MiniCocoon::from_password(b"password", &[1; 32]);
let mut data1 = "my secret data".to_owned().into_bytes();
let _ = cocoon.encrypt(&mut data1)?;

// Another seed: &[2; 32].
let cocoon = MiniCocoon::from_password(b"password", &[2; 32]);
let mut data2 = "my secret data".to_owned().into_bytes();
let _ = cocoon.encrypt(&mut data2)?;

// data1: [23, 217, 251, 151, 179, 62, 85, 15, 253, 92, 192, 112, 200, 52]
// data2: [53, 223, 209, 96, 130, 99, 209, 108, 83, 189, 123, 81, 19, 1]
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21530
- https://github.com/fadeevab/cocoon/issues/22
- https://github.com/fadeevab/cocoon/commit/1b6392173ce35db4736a94b62b2d2973f9a71441
- https://github.com/fadeevab/cocoon/commit
- https://rustsec.org/advisories/RUSTSEC-2023-0068.html
- https://security.snyk.io/vuln/SNYK-RUST-COCOON-6028364
