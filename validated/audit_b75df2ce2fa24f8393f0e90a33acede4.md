Now I have a complete picture. The `paillier_t::convert()` serializes `p` and `q` (the Paillier private factors) when `has_private` is true, and `detach_private_scalar` for ECDSA-2PC copies the full `paillier` object — including the private key — into the output "public" blob. Let me confirm the exact serialization and the `attach_private_scalar` guard that locks in this design.

### Title
`detach_private_scalar` Leaks Paillier Private Key in ECDSA-2PC "Public" Blob, Enabling Private Scalar Recovery — (`File: src/cbmpc/api/ecdsa2pc.cpp`)

---

### Summary

The `coinbase::api::ecdsa_2p::detach_private_scalar` public API is designed for backup/restore flows: it strips the private scalar `x_share` from P1's key blob and returns a "scalar-removed" blob intended for separate storage. However, the implementation copies the full `paillier_t` object — including the Paillier private factors `p` and `q` — into the output blob. Because the blob also retains `c_key = Enc_{paillier}(x_share)`, any party that obtains the output blob can call `paillier.decrypt(c_key)` and recover `x_share` in full. The private scalar is not actually removed; it is merely re-encoded behind a key that is still present in the same blob.

---

### Finding Description

**Root cause — `detach_private_scalar` retains the Paillier private key:**

`src/cbmpc/api/ecdsa2pc.cpp` lines 223–232:

```cpp
key_blob_v1_t pub;
pub.role    = static_cast<uint32_t>(key.role);
pub.curve   = static_cast<uint32_t>(cid);
pub.Q_compressed = key.Q.to_compressed_bin();
pub.x_share = key.paillier.get_N().value();  // sentinel: out-of-range
pub.c_key   = key.c_key;
pub.paillier = key.paillier;                 // ← full private key copied here
out_public_key_blob = coinbase::convert(pub);
``` [1](#0-0) 

The intent of setting `x_share = N` is to make the blob rejected by `sign`/`refresh` APIs. But `c_key` (the Paillier encryption of the original `x_share`) and the full `paillier` object are both preserved.

**Serialization confirms private factors are written:**

`paillier_t::convert` in `src/cbmpc/crypto/base_paillier.cpp`:

```cpp
void paillier_t::convert(coinbase::converter_t& converter) {
  converter.convert(has_private);
  converter.convert(N);
  if (has_private) {
    converter.convert(p);   // ← Paillier prime p
    converter.convert(q);   // ← Paillier prime q
  }
  ...
}
``` [2](#0-1) 

When `has_private == true` (always the case for P1), both `p` and `q` are written into the serialized blob. The `key_blob_v1_t::convert` method unconditionally serializes the `paillier` field: [3](#0-2) 

**`attach_private_scalar` enforces that the Paillier private key must remain in the blob:**

```cpp
const bool paillier_has_private = pub.paillier.has_private_key();
if ((pub.role == 0) != paillier_has_private)
    return coinbase::error(E_FORMAT, "invalid key blob");
...
if (paillier_has_private) {
    const coinbase::crypto::bn_t plain = pub.paillier.decrypt(pub.c_key);
    if (plain != N.mod(x_share))
        return coinbase::error(E_FORMAT, "x_share mismatch key blob");
}
``` [4](#0-3) 

`attach_private_scalar` structurally requires `paillier_has_private == true` for P1 blobs (role == 0), so the design locks in the Paillier private key being present in the "scalar-removed" blob.

**Contrast with other protocols:**

The ECDSA-MP, EdDSA-MP, and Schnorr-MP `detach_private_scalar` APIs explicitly document: *"The public blob is safe to persist as public-only material."* Those protocols carry no Paillier key, so the claim is true. The ECDSA-2PC header omits this claim but also does not warn that the output blob still contains the Paillier private key: [5](#0-4) [6](#0-5) 

---

### Impact Explanation

An attacker who obtains the "scalar-removed" blob output by `detach_private_scalar` for an ECDSA-2PC P1 key can:

1. Deserialize the blob to extract the Paillier private key (`p`, `q`).
2. Call `paillier.decrypt(c_key)` to recover `x_share` — P1's private scalar share — in full.
3. Reconstruct a complete, valid P1 key blob by calling `attach_private_scalar` with the recovered scalar.
4. Impersonate P1 in any subsequent ECDSA-2PC signing or refresh session.

This satisfies the Critical impact tier: *"A shipped API or protocol-peer path lets an attacker recover, forge, or substitute key shares, private scalars, Paillier secrets, or equivalent secret material."*

---

### Likelihood Explanation

The `detach_private_scalar` API is explicitly designed for backup/restore flows (PVE, HSM-backed storage). Callers following the documented pattern — store the "scalar-removed" blob in one location and the private scalar in a more secure location — will inadvertently expose the Paillier private key in the less-protected store. The analogous APIs for ECDSA-MP/EdDSA/Schnorr genuinely produce public-safe blobs, so a developer familiar with those APIs has no reason to treat the ECDSA-2PC output differently.

---

### Recommendation

In `detach_private_scalar` for ECDSA-2PC, replace the full Paillier copy with a public-only copy before serializing the output blob:

```cpp
// Strip private Paillier factors from the output blob.
coinbase::crypto::paillier_t pub_paillier;
pub_paillier.create_pub(key.paillier.get_N().value());
pub.paillier = pub_paillier;
```

`attach_private_scalar` must be updated in parallel: the `(pub.role == 0) != paillier_has_private` guard and the `paillier.decrypt(c_key)` consistency check must be relaxed or replaced with an EC-point-only check (`(x mod q)*G == Qi_self`) for blobs produced by the new `detach_private_scalar`. The `SECURE_USAGE.md` and the `ecdsa_2p.h` header should be updated to explicitly warn that the current output blob is **not** public-safe and must be protected as secret material until the fix is deployed.

---

### Proof of Concept

```cpp
// Attacker has obtained out_public_key_blob from detach_private_scalar.
// Deserialize it.
coinbase::api::ecdsa_2p::key_blob_v1_t stolen;
coinbase::convert(stolen, out_public_key_blob);

// stolen.paillier has_private == true; p and q are present.
// stolen.c_key == Enc_{paillier}(x_share).
coinbase::crypto::bn_t recovered_x_share = stolen.paillier.decrypt(stolen.c_key);

// recovered_x_share == original x_share (P1's private scalar share).
// Attacker can now call attach_private_scalar to reconstruct a fully usable P1 key blob
// and participate in ECDSA-2PC signing as P1.
buf_t qi_self = (recovered_x_share % stolen.paillier.get_N().value() /* mod q */ * G).to_compressed_bin();
buf_t full_key_blob;
coinbase::api::ecdsa_2p::attach_private_scalar(
    out_public_key_blob,
    recovered_x_share.to_bin(),
    qi_self,
    full_key_blob);
// full_key_blob is now a valid, signing-capable P1 key blob.
```

### Citations

**File:** src/cbmpc/api/ecdsa2pc.cpp (L31-31)
```cpp
  void convert(coinbase::converter_t& c) { c.convert(version, role, curve, Q_compressed, x_share, c_key, paillier); }
```

**File:** src/cbmpc/api/ecdsa2pc.cpp (L223-232)
```cpp
  // Produce a v1-format blob with an invalid (out-of-range) scalar share so it is
  // rejected by sign/refresh APIs.
  key_blob_v1_t pub;
  pub.role = static_cast<uint32_t>(key.role);
  pub.curve = static_cast<uint32_t>(cid);
  pub.Q_compressed = key.Q.to_compressed_bin();
  pub.x_share = key.paillier.get_N().value();  // x_share == N is out of range
  pub.c_key = key.c_key;
  pub.paillier = key.paillier;
  out_public_key_blob = coinbase::convert(pub);
```

**File:** src/cbmpc/api/ecdsa2pc.cpp (L257-278)
```cpp
  // Validate Paillier material (c_key + key) is well-formed.
  const bool paillier_has_private = pub.paillier.has_private_key();
  if ((pub.role == 0) != paillier_has_private) return coinbase::error(E_FORMAT, "invalid key blob");

  const auto& N = pub.paillier.get_N();
  if (N.value().get_bits_count() < coinbase::crypto::paillier_t::bit_size)
    return coinbase::error(E_FORMAT, "invalid key blob");
  {
    coinbase::crypto::vartime_scope_t vartime_scope;
    if (pub.paillier.verify_cipher(pub.c_key)) return coinbase::error(E_FORMAT, "invalid key blob");
  }

  // Interpret scalar and ensure it stays in Z_N (matching key blob invariants).
  coinbase::crypto::bn_t x_share = coinbase::crypto::bn_t::from_bin(private_scalar);
  if (!N.is_in_range(x_share)) return coinbase::error(E_FORMAT, "invalid private_scalar");

  // If we have the private key (P1), bind the share to its Paillier encryption.
  if (paillier_has_private) {
    coinbase::crypto::vartime_scope_t vartime_scope;
    const coinbase::crypto::bn_t plain = pub.paillier.decrypt(pub.c_key);
    if (plain != N.mod(x_share)) return coinbase::error(E_FORMAT, "x_share mismatch key blob");
  }
```

**File:** src/cbmpc/crypto/base_paillier.cpp (L15-21)
```cpp
void paillier_t::convert(coinbase::converter_t& converter) {
  converter.convert(has_private);
  converter.convert(N);
  if (has_private) {
    converter.convert(p);
    converter.convert(q);
  }
```

**File:** include/cbmpc/api/ecdsa_2p.h (L54-65)
```text
// Detach the private scalar share from a key blob, producing:
// - a key blob with its private scalar removed, and
// - the private scalar x encoded as a big-endian buffer.
//
// The scalar-removed blob is not usable for signing/refresh until restored with
// `attach_private_scalar`.
//
// Note (ECDSA-2PC encoding):
// - Unlike ECDSA-MP, this scalar encoding is NOT fixed-length. ECDSA-2PC keeps
//   the share as a Paillier-compatible integer representative and it may grow
//   after refresh.
error_t detach_private_scalar(mem_t key_blob, buf_t& out_public_key_blob, buf_t& out_private_scalar);
```

**File:** include/cbmpc/api/ecdsa_mp.h (L101-111)
```text
// Detach the private scalar share from a key blob, producing:
// - a "public" key blob with its private scalar wiped, and
// - the private scalar x encoded as a fixed-length big-endian buffer.
//
// The public blob is safe to persist as public-only material, but is not usable
// for signing/refresh until restored with `attach_private_scalar`.
//
// Output:
// - `out_private_scalar_fixed` length equals the curve order size in bytes
//   (e.g., 32 bytes for secp256k1/p256).
error_t detach_private_scalar(mem_t key_blob, buf_t& out_public_key_blob, buf_t& out_private_scalar_fixed);
```
