Now I have all the information needed. Let me analyze the complete picture.

### Title
Missing `curve.check()` After `from_bin` in `blob_to_keyset` Allows Infinity-Point Injection for OpenSSL Curves, Producing Derived Keys with Wrong Public Key - (`src/cbmpc/api/hd_keyset_ecdsa_2p.cpp`)

---

### Summary

`blob_to_keyset` in `src/cbmpc/api/hd_keyset_ecdsa_2p.cpp` calls `from_bin` for `root_Q_compressed` and `root_K_compressed` but never calls `curve.check()` on the resulting points. For OpenSSL-backed curves (p256, p384), `ecurve_ossl_t::from_bin` explicitly accepts the SEC infinity encoding (an all-zeros buffer of the right size) and returns `SUCCESS`. Because `curve.check()` is never called, the infinity point is not rejected. `derive_keys` then computes `Q_derived = infinity + delta_G = delta_G`, producing a derived key blob whose public key is a random scalar multiple of G rather than the correct HD-derived key.

---

### Finding Description

**The missing guard:**

`blob_to_keyset` in `src/cbmpc/api/hd_keyset_ecdsa_2p.cpp`:

```cpp
error_t rv = keyset.root.Q.from_bin(icurve, blob.root_Q_compressed);
if (rv) return rv;
return keyset.root.K.from_bin(icurve, blob.root_K_compressed);
``` [1](#0-0) 

No `curve.check()` call follows. Compare with the non-HD ECDSA-2PC blob parser, which correctly adds the check:

```cpp
if (const error_t rv = key.Q.from_bin(curve, blob.Q_compressed)) return rv;
if (curve.check(key.Q)) return coinbase::error(E_FORMAT, "invalid key blob");
``` [2](#0-1) 

**`curve.check()` explicitly rejects infinity:**

```cpp
error_t ecurve_t::check(const ecc_point_t& point) const {
  ...
  if (!thread_local_store_allow_ecc_infinity) {
    if (point.is_infinity()) return crypto::error("EC-point is infinity");
  }
  return SUCCESS;
}
``` [3](#0-2) 

**`ecurve_ossl_t::from_bin` accepts infinity for p256/p384:**

```cpp
error_t ecurve_ossl_t::from_bin(ecc_point_t& P, mem_t bin) const {
  if (bin.size > 0 && bin[0] == 0)  // infinity
  {
    if (bin.size != 1 + size() && bin.size != 1 + size() * 2) return coinbase::error(E_FORMAT);
    for (int i = 0; i < bin.size; i++)
      if (bin[i]) return coinbase::error(E_CRYPTO);
    bin.size = 1;
  }
  if (0 >= EC_POINT_oct2point(group, P, bin.data, bin.size, ...)) { ... }
  return SUCCESS;
}
``` [4](#0-3) 

For p256 (`size()` = 32), a 33-byte all-zeros buffer passes all checks, `bin.size` is truncated to 1, and `EC_POINT_oct2point` with `{0x00}` sets P to the point at infinity and returns success. The function returns `SUCCESS` with P = infinity.

**`derive_keys` propagates the infinity point:**

```cpp
ecc_point_t Q = key.root.Q;          // Q = infinity (attacker-injected)
...
ecc_point_t Q_derived = Q + delta_G; // = infinity + delta_G = delta_G
``` [5](#0-4) 

The derived key blob is then serialized with `Q_derived = delta_G` as the public key. [6](#0-5) 

**secp256k1 is NOT affected:** `secp256k1_eckey_pubkey_parse` only accepts inputs with a valid SEC prefix byte (0x02, 0x03, 0x04, 0x06, 0x07). An all-zeros buffer has prefix 0x00, which is rejected immediately. [7](#0-6) 

---

### Impact Explanation

The derived key blob has `Q_derived = delta_G` instead of the correct `Q + delta_G`. The public key in the derived blob does not correspond to the sum of the private key shares held by the two parties. Any ECDSA signatures produced with this derived key will verify against `delta_G` (an attacker-substituted public key), not against the legitimate HD-derived public key. This is a public-key substitution in the HD derivation output: the blob parser and the derivation disagree about Q's validity, and the system accepts and serializes a cryptographically invalid derived key.

This fits the "High" impact category: attacker-controlled blob data is accepted under the wrong key, producing accepted invalid cryptographic output from the HD derivation API.

---

### Likelihood Explanation

The attacker only needs to supply a crafted `keyset_blob` to `derive_ecdsa_2p_keys`. The blob is an opaque byte string accepted at the API boundary. For p256 or p384, crafting the infinity encoding is trivial (33 or 49 all-zero bytes for `root_Q_compressed`). The missing `curve.check()` is a straightforward omission visible by direct comparison with the sibling `ecdsa2pc.cpp` blob parser.

---

### Recommendation

Add `curve.check()` calls immediately after both `from_bin` calls in `blob_to_keyset` in `src/cbmpc/api/hd_keyset_ecdsa_2p.cpp`, mirroring the pattern already used in `src/cbmpc/api/ecdsa2pc.cpp`:

```cpp
error_t rv = keyset.root.Q.from_bin(icurve, blob.root_Q_compressed);
if (rv) return rv;
if (icurve.check(keyset.root.Q)) return coinbase::error(E_FORMAT, "invalid keyset blob Q");

rv = keyset.root.K.from_bin(icurve, blob.root_K_compressed);
if (rv) return rv;
if (icurve.check(keyset.root.K)) return coinbase::error(E_FORMAT, "invalid keyset blob K");
```

The same omission exists in the EdDSA HD keyset parser (`src/cbmpc/api/hd_keyset_eddsa_2p.cpp` lines 78-80), though Ed25519's `from_bin` behavior with infinity should be independently verified. [8](#0-7) 

---

### Proof of Concept

```cpp
// Build a keyset_blob for p256 with root_Q_compressed = 33 zero bytes (SEC infinity encoding).
// Populate all other fields with valid values (valid paillier, valid k_share, valid c_key, etc.)
// so that blob_to_keyset passes all other checks.

keyset_blob_v1_t blob;
blob.version = 1;
blob.role = 1;  // p2
blob.curve = static_cast<uint32_t>(curve_id::p256);
blob.root_Q_compressed = buf_t(33);  // 33 zero bytes
blob.root_Q_compressed.bzero();
// ... populate root_K_compressed, x_share, k_share, paillier, c_key with valid values ...

buf_t crafted_blob = coinbase::convert(blob);

// Call derive_ecdsa_2p_keys with crafted_blob.
// Expected: E_FORMAT (infinity rejected).
// Actual (before fix): SUCCESS, derived key has Q_derived = delta_G.
std::vector<buf_t> out_blobs;
buf_t sid;
error_t rv = coinbase::api::hd_keyset_ecdsa_2p::derive_ecdsa_2p_keys(
    job, crafted_blob, hardened_path, non_hardened_paths, sid, out_blobs);
ASSERT_EQ(rv, E_FORMAT);  // fails before fix
```

### Citations

**File:** src/cbmpc/api/hd_keyset_ecdsa_2p.cpp (L98-100)
```cpp
  error_t rv = keyset.root.Q.from_bin(icurve, blob.root_Q_compressed);
  if (rv) return rv;
  return keyset.root.K.from_bin(icurve, blob.root_K_compressed);
```

**File:** src/cbmpc/api/hd_keyset_ecdsa_2p.cpp (L201-212)
```cpp
  std::vector<buf_t> blobs;
  blobs.resize(derived_keys.size());
  for (size_t i = 0; i < derived_keys.size(); i++) {
    rv = serialize_ecdsa2pc_key_blob(derived_keys[i], blobs[i]);
    if (rv) {
      out_ecdsa_2p_key_blobs.clear();
      return rv;
    }
  }

  out_ecdsa_2p_key_blobs = std::move(blobs);
  return SUCCESS;
```

**File:** src/cbmpc/api/ecdsa2pc.cpp (L81-82)
```cpp
  if (const error_t rv = key.Q.from_bin(curve, blob.Q_compressed)) return rv;
  if (curve.check(key.Q)) return coinbase::error(E_FORMAT, "invalid key blob");
```

**File:** src/cbmpc/crypto/base_ecc.cpp (L317-330)
```cpp
error_t ecurve_ossl_t::from_bin(ecc_point_t& P, mem_t bin) const {
  if (bin.size > 0 && bin[0] == 0)  // infinity
  {
    if (bin.size != 1 + size() && bin.size != 1 + size() * 2) return coinbase::error(E_FORMAT);
    for (int i = 0; i < bin.size; i++)
      if (bin[i]) return coinbase::error(E_CRYPTO);
    bin.size = 1;
  }

  if (0 >= EC_POINT_oct2point(group, P, bin.data, bin.size, bn_t::thread_local_storage_bn_ctx())) {
    return openssl_error("EC_POINT_oct2point error, data-size=" + strext::itoa(bin.size));
  }
  return SUCCESS;
}
```

**File:** src/cbmpc/crypto/base_ecc.cpp (L592-601)
```cpp
error_t ecurve_t::check(const ecc_point_t& point) const {
  if (!point.valid()) return crypto::error("EC-point invalid");
  if (point.get_curve() != *this) return crypto::error("EC-point of wrong curve");
  if (!point.is_in_subgroup()) return crypto::error("EC-point is not on curve");

  if (!thread_local_store_allow_ecc_infinity) {
    if (point.is_infinity()) return crypto::error("EC-point is infinity");
  }
  return SUCCESS;
}
```

**File:** src/cbmpc/protocol/hd_keyset_ecdsa_2p.cpp (L113-154)
```cpp
  ecc_point_t Q = key.root.Q;

  // This is VRF-Compute-2P in the spec
  const int delta_size = curve.size() + 16;  // 256 + 128 bits
  ecc_point_t Z1, Z2;
  ecc_point_t P = crypto::ro::hash_curve(hardened_path.get()).curve(curve);
  ecc_point_t Z_share = k_share * P;
  if (job.is_p1())
    Z1 = Z_share;
  else
    Z2 = Z_share;
  zk::dh_t zk_dh1, zk_dh2;

  if (job.is_p1()) {
    zk_dh1.prove(P, K_share, Z1, k_share, sid, 1);
  }

  if (rv = job.p1_to_p2(Z1, zk_dh1)) return rv;

  if (job.is_p2()) {
    // Verification that Z1 is valid is done in the verify function
    if (rv = zk_dh1.verify(P, other_K_share, Z1, sid, 1)) return rv;
    zk_dh2.prove(P, K_share, Z2, k_share, sid, 2);
  }

  if (rv = job.p2_to_p1(Z2, zk_dh2)) return rv;

  if (job.is_p1()) {
    if (rv = zk_dh2.verify(P, other_K_share, Z2, sid, 2)) return rv;
  }
  ecc_point_t Z = Z1 + Z2;
  // The rest of Hard-Derive-2P
  // The rest of Hard-Derive-2P
  buf_t y = crypto::ro::hash_string(Z).bitlen(bytes_to_bits(delta_size) + 256);
  bn_t delta = bn_t::from_bin(y.take(delta_size)) % q;
  buf_t chain_code = y.skip(delta_size);

  int n_hd_paths = (int)non_hardened_paths.size();
  derived_keys.resize(n_hd_paths);

  ecc_point_t delta_G = delta * G;
  ecc_point_t Q_derived = Q + delta_G;
```

**File:** vendors/secp256k1/src/eckey_impl.h (L17-35)
```text
static int secp256k1_eckey_pubkey_parse(secp256k1_ge *elem, const unsigned char *pub, size_t size) {
    if (size == 33 && (pub[0] == SECP256K1_TAG_PUBKEY_EVEN || pub[0] == SECP256K1_TAG_PUBKEY_ODD)) {
        secp256k1_fe x;
        return secp256k1_fe_set_b32_limit(&x, pub+1) && secp256k1_ge_set_xo_var(elem, &x, pub[0] == SECP256K1_TAG_PUBKEY_ODD);
    } else if (size == 65 && (pub[0] == SECP256K1_TAG_PUBKEY_UNCOMPRESSED || pub[0] == SECP256K1_TAG_PUBKEY_HYBRID_EVEN || pub[0] == SECP256K1_TAG_PUBKEY_HYBRID_ODD)) {
        secp256k1_fe x, y;
        if (!secp256k1_fe_set_b32_limit(&x, pub+1) || !secp256k1_fe_set_b32_limit(&y, pub+33)) {
            return 0;
        }
        secp256k1_ge_set_xy(elem, &x, &y);
        if ((pub[0] == SECP256K1_TAG_PUBKEY_HYBRID_EVEN || pub[0] == SECP256K1_TAG_PUBKEY_HYBRID_ODD) &&
            secp256k1_fe_is_odd(&y) != (pub[0] == SECP256K1_TAG_PUBKEY_HYBRID_ODD)) {
            return 0;
        }
        return secp256k1_ge_is_valid_var(elem);
    } else {
        return 0;
    }
}
```

**File:** src/cbmpc/api/hd_keyset_eddsa_2p.cpp (L78-80)
```cpp
  error_t rv = keyset.root.Q.from_bin(keyset.curve, blob.root_Q_compressed);
  if (rv) return rv;
  return keyset.root.K.from_bin(keyset.curve, blob.root_K_compressed);
```
