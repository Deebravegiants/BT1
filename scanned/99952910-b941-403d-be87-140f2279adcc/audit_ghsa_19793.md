# [M] AEADs/ascon-aead: Plaintext exposed in decrypt_in_place_detached even on tag verification failure

## Summary
Severity: Medium
Advisory: GHSA-r38m-44fw-h886
CVE: CVE-2025-27498
CWE: CWE-347
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:L/AC:H/AT:N/PR:N/UI:A/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-03-03
Source: https://github.com/advisories/GHSA-r38m-44fw-h886
Type: github-advisory

## Affected
- crates.io: `ascon_aead` — affected >=0 <0.4.3

## Details
### Summary
In `decrypt_in_place_detached`, the decrypted ciphertext (which is the correct ciphertext) is exposed even if the tag is incorrect.

### Details
This is because in [decrypt_inplace](https://github.com/RustCrypto/AEADs/blob/8cda109f1128c4c7953a0bb0f53e1056d537e462/ascon-aead/src/asconcore.rs#L350-L364) in asconcore.rs, tag verification causes an error to be returned with the plaintext contents still in `buffer`. The root cause of this vulnerability is similar to https://github.com/RustCrypto/AEADs/security/advisories/GHSA-423w-p2w9-r7vq

### PoC
```rust
use ascon_aead::Tag;
use ascon_aead::{Ascon128, Key, Nonce};
use ascon_aead::aead::{AeadInPlace, KeyInit};

fn main() {

    let key = Key::<Ascon128>::from_slice(b"very secret key.");
    let cipher = Ascon128::new(key);

    let nonce = Nonce::<Ascon128>::from_slice(b"unique nonce 012"); // 128-bits; unique per message

    let mut buffer: Vec<u8> = Vec::new(); // Buffer needs 16-bytes overhead for authentication tag
    buffer.extend_from_slice(b"plaintext message");

    // Encrypt `buffer` in-place detached, replacing the plaintext contents with ciphertext
    cipher.encrypt_in_place_detached(nonce, b"", &mut buffer).expect("encryption failure!");
    
    // Decrypt `buffer` in-place with the wrong tag, ignoring the decryption error
    let _ = cipher.decrypt_in_place_detached(nonce, b"", &mut buffer, Tag::<Ascon128>::from_slice(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"));

    assert_eq!(&buffer, b"plaintext message");
}
```
### Impact
If a program continues to use the result of `decrypt_in_place_detached` after a decryption failure, the result will be unauthenticated. This may permit some forms of chosen ciphertext attacks (CCAs).

## References
- https://github.com/RustCrypto/AEADs/security/advisories/GHSA-r38m-44fw-h886
- https://nvd.nist.gov/vuln/detail/CVE-2025-27498
- https://github.com/RustCrypto/AEADs/commit/d1d749ba57e38e65b0e037cd744d0b17f7254037
- https://github.com/RustCrypto/AEADs
