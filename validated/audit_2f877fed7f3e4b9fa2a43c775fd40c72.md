### Title
ECDSA-2PC `detach_private_scalar` Retains Paillier Private Key in "Scalar-Removed" Blob, Enabling Full Key Share Recovery - (File: src/cbmpc/api/ecdsa2pc.cpp)

### Summary
`coinbase::api::ecdsa_2p::detach_private_scalar` (and its C ABI wrapper `cbmpc_ecdsa_2p_detach_private_scalar`) is designed to split a key blob into a "scalar-removed" blob plus the raw private scalar for backup workflows. However, the scalar-removed blob it produces for P1 still contains the **full Paillier private key** (primes `p` and `q`) together with `c_key` — the Paillier encryption of P1's ECDSA scalar share. Any party that obtains this blob can immediately decrypt `c_key` to recover P1's complete ECDSA private scalar share, defeating the purpose of the detach operation.

### Finding Description

The ECDSA-2PC key blob structure is defined in `src/cbmpc/api/ecdsa2pc.cpp`:

```cpp
struct key_blob_v1_t {
  uint32_t version = key_blob_version_v1;
  uint32_t role = 0;
  uint32_t curve = 0;
  buf_t Q_compressed;
  coinbase::crypto::bn_t x_share;   // P1's ECDSA scalar share
  coinbase::crypto::bn_t c_key;     // Enc_{paillier}(x_share)
  coinbase::crypto::paillier_t paillier;  // full Paillier key (p,q) for P1
  void convert(coinbase::converter_t& c) { c.convert(version, role, curve, Q_compressed, x_share, c_key, paillier); }
};
``` [1](#0-0) 

`detach_private_scalar` replaces `x_share` with an out-of-range sentinel (`N`) to block signing, but copies the full `paillier` object — including the private primes — verbatim into the output blob:

```cpp
key_blob_v1_t pub;
pub.x_share = key.paillier.get_N().value();  // sentinel: out of range
pub.c_key   = key.c_key;                     // still present
pub.paillier = key.paillier;                 // FULL private key (p, q) retained
out_public_key_blob = coinbase::convert(pub);
``` [2](#0-1) 

`paillier_t::convert` serializes `p` and `q` whenever `has_private` is true:

```cpp
void paillier_t::convert(coinbase::converter_t& converter) {
  converter.convert(has_private);
  converter.convert(N);
  if (has_private) {
    converter.convert(p);
    converter.convert(q);
  }
  ...
}
``` [3](#0-2) 

So the serialized "scalar-removed" blob for P1 contains `has_private=true`, `N`, `p`, `q`, and `c_key`. With `p` and `q` in hand, decrypting `c_key` directly yields `x_share`.

The output parameter is named `out_public_key_blob` in both the C++ API and the C ABI: [4](#0-3) [5](#0-4) 

The ECDSA-MP counterpart explicitly states "The public blob is safe to persist as public-only material": [6](#0-5) 

This cross-API naming consistency creates a direct expectation that the ECDSA-2PC scalar-removed blob is equally safe to store unencrypted — but it is not.

### Impact Explanation

An attacker who obtains the scalar-removed blob for P1 can:
1. Deserialize the blob to extract `p`, `q`, and `c_key`.
2. Reconstruct the Paillier private key from `p` and `q`.
3. Call `paillier.decrypt(c_key)` to recover `x_share` — P1's full ECDSA private scalar share.

This satisfies the Critical impact tier: a shipped public API path lets an attacker recover a private scalar and Paillier secret from a blob the API explicitly names "public." With P1's scalar share recovered, the attacker can participate in or fully simulate P1's role in any subsequent ECDSA-2PC signing session.

### Likelihood Explanation

The `detach_private_scalar` / `attach_private_scalar` pair is the documented mechanism for PVE-based backup workflows (README, SECURE_USAGE.md). Callers following the backup pattern will naturally store the scalar-removed blob at rest — potentially without encryption — because the parameter name `out_public_key_blob` and the parallel ECDSA-MP documentation both signal it is safe to do so. The C API comment "Detach a key blob into a scalar-removed blob + private scalar" does not warn that the scalar-removed blob still contains the Paillier private key. [7](#0-6) 

### Recommendation

In `ecdsa_2p::detach_private_scalar`, replace the full Paillier copy with a public-only copy:

```cpp
// Instead of: pub.paillier = key.paillier;
coinbase::crypto::paillier_t pub_paillier;
pub_paillier.create_pub(key.paillier.get_N().value());
pub.paillier = pub_paillier;
// Also clear c_key since it is only needed for signing (which requires x_share):
pub.c_key = coinbase::crypto::bn_t{};
```

Additionally, update the API documentation to explicitly state that the scalar-removed blob for ECDSA-2PC must still be treated as secret material (unlike ECDSA-MP), and add a note distinguishing the two protocols' blob confidentiality requirements.

### Proof of Concept

```
// Attacker receives out_public_key_blob from a caller who stored it unencrypted.
key_blob_v1_t stolen;
coinbase::convert(stolen, out_public_key_blob);   // deserialize

// stolen.paillier has has_private=true, p, q present.
// stolen.c_key = Enc_{paillier}(x_share).
coinbase::crypto::bn_t recovered_x = stolen.paillier.decrypt(stolen.c_key);
// recovered_x == P1's original x_share (mod N).
// Attacker now holds P1's ECDSA private scalar share.
```

Entry path: `cbmpc_ecdsa_2p_detach_private_scalar` (C ABI) → `coinbase::api::ecdsa_2p::detach_private_scalar` (C++ API) → scalar-removed blob serialized with full Paillier private key. [8](#0-7)

### Citations

**File:** src/cbmpc/api/ecdsa2pc.cpp (L21-32)
```cpp
struct key_blob_v1_t {
  uint32_t version = key_blob_version_v1;
  uint32_t role = 0;   // 0=p1, 1=p2
  uint32_t curve = 0;  // coinbase::api::curve_id

  buf_t Q_compressed;
  coinbase::crypto::bn_t x_share;
  coinbase::crypto::bn_t c_key;
  coinbase::crypto::paillier_t paillier;

  void convert(coinbase::converter_t& c) { c.convert(version, role, curve, Q_compressed, x_share, c_key, paillier); }
};
```

**File:** src/cbmpc/api/ecdsa2pc.cpp (L225-232)
```cpp
  key_blob_v1_t pub;
  pub.role = static_cast<uint32_t>(key.role);
  pub.curve = static_cast<uint32_t>(cid);
  pub.Q_compressed = key.Q.to_compressed_bin();
  pub.x_share = key.paillier.get_N().value();  // x_share == N is out of range
  pub.c_key = key.c_key;
  pub.paillier = key.paillier;
  out_public_key_blob = coinbase::convert(pub);
```

**File:** src/cbmpc/crypto/base_paillier.cpp (L15-39)
```cpp
void paillier_t::convert(coinbase::converter_t& converter) {
  converter.convert(has_private);
  converter.convert(N);
  if (has_private) {
    converter.convert(p);
    converter.convert(q);
  }

  if (!converter.is_write()) {
    if (converter.is_error()) return;
    if (N.get_bits_count() > bit_size) {
      converter.set_error();
      return;
    }
    if (has_private) {
      // This path rebuilds a private key from serialized state without semantically validating `p`/`q`.
      // It is intended for trusted local blobs.
      update_private();
    } else {
      // This path only rebuilds cached public state from the deserialized modulus.
      // `mod_t::convert()` already enforces the basic modulus representation, but callers are still responsible
      // for any higher-level/context-specific validation at the boundary after deserialization.
      update_public();
    }
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

**File:** include/cbmpc/c_api/ecdsa_2p.h (L63-75)
```text
// Detach a key blob into a scalar-removed blob + private scalar.
//
// Notes:
// - Unlike ECDSA-MP, the scalar encoding is NOT fixed-length: after refresh,
//   ECDSA-2PC keeps the share as a Paillier-compatible integer representative and
//   it may grow.
//
// Ownership:
// - On success, `out_public_key_blob->data` and `out_private_scalar->data` are
//   allocated by the library and must be freed with `cbmpc_cmem_free(...)`.
// - On failure, outputs are set to `{NULL, 0}`.
cbmpc_error_t cbmpc_ecdsa_2p_detach_private_scalar(cmem_t key_blob, cmem_t* out_public_key_blob,
                                                   cmem_t* out_private_scalar);
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

**File:** README.md (L133-136)
```markdown

- If a party loses its only local `key_blob` / `keyset_blob` and no protected backup exists, recovery may depend on the protocol and access structure; do not assume `cb-mpc` can recreate that party-local secret material for you.
- If recovery is a requirement, the application should maintain encrypted backups of each party's local secret material. For supported signing key types, the relevant public API exposes `detach_private_scalar`, `get_public_share_compressed`, and `attach_private_scalar` helpers for application-managed backup and restore flows, including verifiable backup schemes such as publicly verifiable encryption (PVE).
- Use the corresponding `refresh*` APIs when you want fresh shares for the same (combined) key; if your operational policy requires replacing the key entirely, run a new `dkg*` flow and migrate in the application layer.
```

**File:** src/cbmpc/c_api/ecdsa2pc.cpp (L189-234)
```cpp
cbmpc_error_t cbmpc_ecdsa_2p_detach_private_scalar(cmem_t key_blob, cmem_t* out_public_key_blob,
                                                   cmem_t* out_private_scalar) {
  try {
    if (!out_public_key_blob || !out_private_scalar) return E_BADARG;
    *out_public_key_blob = cmem_t{nullptr, 0};
    *out_private_scalar = cmem_t{nullptr, 0};
    const auto vkb = validate_cmem(key_blob);
    if (vkb) return vkb;

    coinbase::buf_t public_blob;
    coinbase::buf_t private_scalar;
    const coinbase::error_t rv =
        coinbase::api::ecdsa_2p::detach_private_scalar(view_cmem(key_blob), public_blob, private_scalar);
    if (rv) return rv;

    const auto r1 = alloc_cmem_from_buf(public_blob, out_public_key_blob);
    if (r1) return r1;
    const auto r2 = alloc_cmem_from_buf(private_scalar, out_private_scalar);
    if (r2) {
      cbmpc_cmem_free(*out_public_key_blob);
      *out_public_key_blob = cmem_t{nullptr, 0};
      return r2;
    }
    return CBMPC_SUCCESS;
  } catch (const std::bad_alloc&) {
    if (out_public_key_blob) {
      cbmpc_cmem_free(*out_public_key_blob);
      *out_public_key_blob = cmem_t{nullptr, 0};
    }
    if (out_private_scalar) {
      cbmpc_cmem_free(*out_private_scalar);
      *out_private_scalar = cmem_t{nullptr, 0};
    }
    return E_INSUFFICIENT;
  } catch (...) {
    if (out_public_key_blob) {
      cbmpc_cmem_free(*out_public_key_blob);
      *out_public_key_blob = cmem_t{nullptr, 0};
    }
    if (out_private_scalar) {
      cbmpc_cmem_free(*out_private_scalar);
      *out_private_scalar = cmem_t{nullptr, 0};
    }
    return E_GENERAL;
  }
}
```
