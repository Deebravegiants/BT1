### Title
`detach_private_scalar` Retains Paillier Private Key Alongside `c_key` in "Public" Blob, Enabling Full Recovery of P1's ECDSA-2PC Private Scalar - (File: `src/cbmpc/api/ecdsa2pc.cpp`)

### Summary

The public API function `ecdsa_2p::detach_private_scalar` is documented as producing a "public" key blob that is "safe to persist as public-only material." However, the output blob retains both `c_key` (the Paillier encryption of the private scalar `x_share`) and the full Paillier private key (`p`, `q`, `phi_N`, etc.) in the same serialized structure. Any party who obtains this "public" blob can immediately decrypt `c_key` using the embedded Paillier private key to recover the original private scalar — the exact "key stored alongside encrypted data" pattern.

### Finding Description

In `src/cbmpc/api/ecdsa2pc.cpp`, the `key_blob_v1_t` structure for ECDSA-2PC P1 contains three co-located secrets:

```cpp
struct key_blob_v1_t {
  buf_t Q_compressed;
  coinbase::crypto::bn_t x_share;        // P1's private scalar (plaintext)
  coinbase::crypto::bn_t c_key;          // Paillier encryption of x_share
  coinbase::crypto::paillier_t paillier; // Paillier key — includes private factors for P1
  ...
};
``` [1](#0-0) 

The `detach_private_scalar` function is intended to separate the private scalar for backup/restore flows. It invalidates `x_share` by setting it to `N` (out of range), but it copies both `c_key` and the full `paillier` object (including private key) verbatim into the output "public" blob:

```cpp
pub.x_share = key.paillier.get_N().value();  // x_share == N is out of range
pub.c_key = key.c_key;        // c_key retained
pub.paillier = key.paillier;  // Paillier private key retained
out_public_key_blob = coinbase::convert(pub);
``` [2](#0-1) 

The `attach_private_scalar` function structurally enforces that the Paillier private key must remain in the "public" blob for P1 (role=0), because it uses it to verify consistency:

```cpp
const bool paillier_has_private = pub.paillier.has_private_key();
if ((pub.role == 0) != paillier_has_private) return coinbase::error(E_FORMAT, "invalid key blob");
...
const coinbase::crypto::bn_t plain = pub.paillier.decrypt(pub.c_key);
if (plain != N.mod(x_share)) return coinbase::error(E_FORMAT, "x_share mismatch key blob");
``` [3](#0-2) 

The API documentation for `detach_private_scalar` explicitly states:

> "The public blob is safe to persist as public-only material, but is not usable for signing/refresh until restored with `attach_private_scalar`." [2](#0-1) 

This claim is false. The "public" blob for P1 necessarily contains the Paillier private key, which decrypts `c_key` to yield the original `x_share`. The library's own `SECURE_USAGE.md` acknowledges that blobs "often contain secret key material (private key shares, Paillier secret keys, etc.)" and must be treated as raw private keys — but this contradicts the `detach_private_scalar` API contract. [4](#0-3) 

The same structural issue exists in the HD keyset ECDSA-2PC blob, which also co-locates `x_share`, `c_key`, and the Paillier private key in `keyset_blob_v1_t`: [5](#0-4) 

### Impact Explanation

An attacker who obtains the "public" blob output of `detach_private_scalar` (which the API documents as safe to persist) can:

1. Deserialize the blob to extract `c_key` and `paillier` (with private factors `p`, `q`, `phi_N`).
2. Call `paillier.decrypt(c_key)` to recover the original `x_share` — P1's private scalar share.
3. With `x_share` and the Paillier private key, the attacker has P1's complete key material and can impersonate P1 in any future signing session, or (combined with P2's share) reconstruct the full ECDSA private key.

This breaks the MPC security model: the entire purpose of the 2PC split is that no single party holds enough material to sign alone. The false "public-safe" claim causes applications to store this blob in less-protected storage (e.g., a database, backup service, or audit log), creating a single point of compromise.

### Likelihood Explanation

The false API documentation is the direct trigger. Any integrating application that follows the documented backup/restore flow — calling `detach_private_scalar`, storing the "public" blob in lower-trust storage, and keeping only the `private_scalar` in a secure enclave — will inadvertently expose P1's full key material. The entry path is the shipped public C++ API (`coinbase::api::ecdsa_2p::detach_private_scalar`) and the C stable ABI (`cbmpc_ecdsa_2p_detach_private_scalar`), both reachable without any threshold collusion.

### Recommendation

1. **Remove the Paillier private key from the "public" blob.** `detach_private_scalar` should strip the private factors from `paillier` before serializing the output, retaining only the public modulus `N`.
2. **Fix `attach_private_scalar` to not require the Paillier private key.** The consistency check `paillier.decrypt(c_key) == x_share` can be replaced with the equivalent public-key check: verify that `c_key` is a valid Paillier ciphertext under the public key, and that `x_share * G == Qi_self` (already performed). The Paillier decryption check is redundant given the EC point binding.
3. **Update the API documentation** to accurately describe what secret material each blob variant contains until the fix is deployed.

### Proof of Concept

```cpp
// Step 1: P1 runs DKG and obtains a full key blob.
buf_t key_blob;
coinbase::api::ecdsa_2p::dkg(job_p1, coinbase::api::curve_id::secp256k1, key_blob);

// Step 2: P1 calls detach_private_scalar, believing out_public_blob is safe to persist.
buf_t out_public_blob, out_private_scalar;
coinbase::api::ecdsa_2p::detach_private_scalar(key_blob, out_public_blob, out_private_scalar);
// out_public_blob is stored in lower-trust storage (e.g., a backup DB).

// Step 3: Attacker obtains out_public_blob and parses it.
// (key_blob_v1_t is the internal struct; attacker replicates the converter layout)
key_blob_v1_t pub;
coinbase::convert(pub, out_public_blob);

// Step 4: pub.paillier.has_private_key() == true (enforced by attach_private_scalar contract).
// Attacker decrypts c_key to recover the original x_share.
coinbase::crypto::bn_t recovered_x_share = pub.paillier.decrypt(pub.c_key);
// recovered_x_share == original x_share (P1's private scalar share).
// The attacker now holds P1's complete key material.
``` [6](#0-5) [7](#0-6)

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

**File:** src/cbmpc/api/ecdsa2pc.cpp (L208-234)
```cpp
error_t detach_private_scalar(mem_t key_blob, buf_t& out_public_key_blob, buf_t& out_private_scalar) {
  if (const error_t rv = coinbase::api::detail::validate_mem_arg_max_size(key_blob, "key_blob",
                                                                          coinbase::api::detail::MAX_OPAQUE_BLOB_SIZE))
    return rv;
  coinbase::mpc::ecdsa2pc::key_t key;
  error_t rv = deserialize_key_blob(key_blob, key);
  if (rv) return rv;

  curve_id cid;
  if (!from_internal_curve(key.curve, cid)) return coinbase::error(E_BADARG, "unsupported curve");
  if (cid == curve_id::ed25519) return coinbase::error(E_BADARG, "unsupported curve");

  // Variable-length big-endian encoding (may grow after refresh).
  out_private_scalar = key.x_share.to_bin();

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
  return SUCCESS;
}
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

**File:** SECURE_USAGE.md (L91-98)
```markdown
Many public APIs return versioned, opaque `buf_t` blobs (e.g., `key_blob`, `keyset_blob`, TDH2 `private_share`, PVE base-PKE `dk` blobs). These blobs are designed for portability across process restarts, but they often contain *secret key material* (private key shares, Paillier secret keys, etc.).

Important implications:

- Treat these blobs as you would treat a raw private key: do not log them, do not send them over the network, and avoid writing them to disk unless necessary.
- In particular, do not send a party's `key_blob` / `keyset_blob` to the other MPC party: these blobs are private key *shares* and often include auxiliary secrets (e.g., Paillier secret keys). Sharing them breaks the trust model.
- The library does not encrypt or authenticate these blobs for you. If you persist them, protect them with an application-managed AEAD (e.g., XChaCha20-Poly1305 or AES-256-GCM) and bind associated data such as: protocol name, curve id, blob version, and the expected party identity (role / party name).
- Prefer encrypting these blobs at rest via envelope encryption: keep the wrapping/encryption key in an HSM/secure enclave or managed KMS (outside the host) and store only AEAD-encrypted blobs on disk. Ensure crash dumps / core dumps and crash reporting cannot exfiltrate plaintext secret material.
```

**File:** src/cbmpc/api/hd_keyset_ecdsa_2p.cpp (L57-72)
```cpp
struct keyset_blob_v1_t {
  uint32_t version = keyset_blob_version_v1;
  uint32_t role = 0;   // 0=p1, 1=p2
  uint32_t curve = 0;  // coinbase::api::curve_id

  buf_t root_Q_compressed;
  buf_t root_K_compressed;
  coinbase::crypto::bn_t x_share;
  coinbase::crypto::bn_t k_share;
  coinbase::crypto::paillier_t paillier;
  coinbase::crypto::bn_t c_key;

  void convert(coinbase::converter_t& c) {
    c.convert(version, role, curve, root_Q_compressed, root_K_compressed, x_share, k_share, paillier, c_key);
  }
};
```
