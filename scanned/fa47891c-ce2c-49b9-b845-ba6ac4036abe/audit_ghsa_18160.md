# [M] httpsig-rs: HMAC verification is vulnerable to timing attack

## Summary
Severity: Medium
Advisory: GHSA-q7pg-9pr4-mrp2
CVE: CVE-2025-59058
CWE: CWE-208
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-09-12
Source: https://github.com/advisories/GHSA-q7pg-9pr4-mrp2
Type: github-advisory

## Affected
- crates.io: `httpsig` — affected >=0 <0.0.19

## Details
### Summary
HMAC signature comparison is not timing-safe and is vulnerable to timing attacks.

### Details
`SharedKey::sign()` returns a `Vec<u8>` which has a non-constant-time equality implementation.

`Hmac::finalize()` returns a constant-time wrapper ([`CtOutput`](https://docs.rs/digest/0.10.7/digest/struct.CtOutput.html)) which was discarded. Alternatively, `Hmac` has a constant-time `verify()` method.

The problem reported here is due to the following lines in `SharedKey::sign()` of the previous code:
```rust
let mut mac = HmacSha256::new_from_slice(key).unwrap();
mac.update(data);
Ok(mac.finalize().into_bytes().to_vec())
```
and the merged update changes the third line to directly verify with `verify_slice`.

### Impact

Anyone who uses HS256 signature verification is vulnerably to Timing Attack that allows the attacker to forge a signature.

## References
- https://github.com/junkurihara/httpsig-rs/security/advisories/GHSA-q7pg-9pr4-mrp2
- https://nvd.nist.gov/vuln/detail/CVE-2025-59058
- https://github.com/junkurihara/httpsig-rs/commit/fc095b6ce6043bb808f5d9c4379cf697899cb458
- https://github.com/junkurihara/httpsig-rs
