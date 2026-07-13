I have traced the full code path. Let me now deliver the analysis.

**Key facts established:**

1. `blob_to_keyset` in `src/cbmpc/api/hd_keyset_eddsa_2p.cpp` validates `x_share ∈ [1, q-1]` and decodes `root_Q_compressed` as a valid curve point, but performs **no** `x_share * G == Q_share` consistency check. [1](#0-0) 

2. By contrast, `ecdsa_mp::deserialize_key_blob` explicitly checks `blob.x_share * G != it_self->second` and rejects on mismatch. [2](#0-1) 

3. `derive_keys` reads `Q = key.root.Q` verbatim from the deserialized keyset and computes `Q_derived = Q + delta*G`. The `delta` is derived from the VRF over `k_share` (not `x_share`), and the ZK-DH proofs only bind `k_share` to `K`, not `x_share` to `Q`. [3](#0-2) 

4. The ZK-DH proof verifies `Z_share = k_share * P` against `other_K_share = K - k_share*G` from the **honest party's own blob**, so a corrupted `root_K_compressed` would be caught. But there is no analogous proof binding `x_share` to `Q`. [4](#0-3) 

5. P1 (attacker) and P2 (honest) each use their **own** `root_Q_compressed` to compute `Q_derived`. Since `delta` is the same for both (derived from the shared VRF output `Z = Z1 + Z2`), a corrupted `Q'` in P1's blob causes P1 to compute `Q_derived_P1 = Q' + delta*G` while P2 computes `Q_derived_P2 = Q_real + delta*G`. These differ whenever `Q' ≠ Q_real`. [5](#0-4) 

6. The output derived key blobs are serialized directly from the internal `eddsa2pc::key_t` without any post-derivation consistency check. [6](#0-5) 

---

### Title
Missing `x_share * G == Q_share` Binding Check in `blob_to_keyset` Allows Attacker to Inject Inconsistent Root Public Key, Causing Honest-Party Divergence on Derived EdDSA-2PC Keys — (`src/cbmpc/api/hd_keyset_eddsa_2p.cpp`)

### Summary

`blob_to_keyset` validates that `x_share ∈ [1, q-1]` and that `root_Q_compressed` decodes to a valid curve point, but never checks that `x_share * G` equals the party's share of `Q`. An attacker who controls their own keyset blob can supply an arbitrary `root_Q_compressed` encoding a point `Q'` unrelated to their actual `x_share`. When `derive_eddsa_2p_keys` is called, both parties compute the same `delta` from the VRF but apply it to their own (potentially different) `Q`, producing derived key blobs with different public keys. The honest party accepts the derived key without error, but the resulting signature fails external verification.

### Finding Description

**Entrypoint:** `coinbase::api::hd_keyset_eddsa_2p::derive_eddsa_2p_keys` [7](#0-6) 

**Deserialization:** `deserialize_keyset_blob` → `blob_to_keyset`. The function checks:
- `blob.role ≤ 1` ✓
- `blob.curve == ed25519` ✓
- `q.is_in_range(blob.x_share)` ✓
- `q.is_in_range(blob.k_share)` ✓
- `keyset.root.Q.from_bin(...)` succeeds (valid curve point) ✓
- **Missing:** `blob.x_share * G == Q_share` ✗ [1](#0-0) 

**Protocol execution:** `key_share_eddsa_hdmpc_2p_t::derive_keys` reads `Q = key.root.Q` directly and computes `Q_derived = Q + delta*G`. The ZK-DH proofs bind `k_share` to `K` (via `other_K_share` from the honest party's blob), but there is no proof binding `x_share` to `Q`. Both parties compute the same `delta` from the shared VRF output, but apply it to their own `Q`. [8](#0-7) 

**Contrast:** `ecdsa_mp::deserialize_key_blob` explicitly rejects blobs where `blob.x_share * G != it_self->second`, closing the same gap for the ECDSA-MP path. [2](#0-1) 

### Impact Explanation

- P1 (attacker) crafts a blob with `x_share = s` (valid) and `root_Q_compressed = Q'` where `Q' ≠ s*G + x_share_P2*G`.
- Both parties run `derive_eddsa_2p_keys`. The VRF produces the same `delta` for both.
- P1 computes `Q_derived_P1 = Q' + delta*G + non_hard_delta*G`.
- P2 computes `Q_derived_P2 = Q_real + delta*G + non_hard_delta*G`.
- The two derived key blobs carry different `Q` values: honest-party divergence.
- When signing, the combined private key is `(s + delta + non_hard_delta) + x_share_P2`, whose corresponding public key is `(s + delta + non_hard_delta + x_share_P2)*G`. This matches neither `Q_derived_P1` nor `Q_derived_P2` in general, so signatures fail external verification.
- P2 accepts the derived key and completes signing without any error, producing an invalid signature.

### Likelihood Explanation

The attacker need only serialize a well-formed keyset blob (correct version, curve, role, valid scalar, valid curve point) with a mismatched `root_Q_compressed`. No cryptographic forgery is required. The API is reachable from any caller who holds a keyset blob for their own party.

### Recommendation

Add a scalar-to-point binding check in `blob_to_keyset` analogous to the check in `ecdsa_mp::deserialize_key_blob`:

```cpp
// After decoding x_share and root_Q_compressed:
const auto& G = keyset.curve.generator();
ecc_point_t Q_share = blob.x_share * G;
// Compute peer's Q_share = keyset.root.Q - Q_share and verify consistency,
// OR store and validate Q_share separately in the blob format.
```

Because the blob stores only the combined `Q` (not per-party `Q_share`), the simplest fix is to also store `Q_share_compressed` in the blob (as `ecdsa_mp` does via `Qis_compressed`) and check `blob.x_share * G == Q_share` on deserialization.

### Proof of Concept

```
// Party P1 (attacker): craft blob with x_share=1, root_Q_compressed=2*G
keyset_blob_v1_t crafted;
crafted.version = 1;
crafted.role = 0;  // p1
crafted.curve = static_cast<uint32_t>(curve_id::ed25519);
crafted.x_share = bn_t(1);
crafted.k_share = /* any valid k_share */;
crafted.root_Q_compressed = (bn_t(2) * G).to_compressed_bin();  // 2*G, not x1*G + x2*G
crafted.root_K_compressed = /* correct K */;
buf_t p1_blob = coinbase::convert(crafted);

// Party P2 (honest): has correct blob from DKG
buf_t p2_blob = /* result of hd_keyset_eddsa_2p::dkg */;

// Both call derive_eddsa_2p_keys with the same hardened/non-hardened paths
// P1 derives Q_derived_P1 = 2*G + delta*G + nh_delta*G
// P2 derives Q_derived_P2 = Q_real + delta*G + nh_delta*G
// Assert: get_public_key_compressed(derived1[0]) != get_public_key_compressed(derived2[0])
// Assert: eddsa_2p::sign produces a signature that fails verification against derived2[0]'s Q
```

### Citations

**File:** src/cbmpc/api/hd_keyset_eddsa_2p.cpp (L63-81)
```cpp
static error_t blob_to_keyset(const keyset_blob_v1_t& blob, coinbase::mpc::key_share_eddsa_hdmpc_2p_t& keyset) {
  if (blob.role > 1) return coinbase::error(E_FORMAT, "invalid keyset blob role");
  if (static_cast<curve_id>(blob.curve) != curve_id::ed25519)
    return coinbase::error(E_FORMAT, "invalid keyset blob curve");

  keyset.party_index = static_cast<coinbase::mpc::party_idx_t>(blob.role);
  keyset.curve = coinbase::crypto::curve_ed25519;

  const coinbase::crypto::mod_t& q = keyset.curve.order();
  if (!q.is_in_range(blob.x_share)) return coinbase::error(E_FORMAT, "invalid keyset blob");
  if (!q.is_in_range(blob.k_share)) return coinbase::error(E_FORMAT, "invalid keyset blob");

  keyset.root.x_share = blob.x_share;
  keyset.root.k_share = blob.k_share;

  error_t rv = keyset.root.Q.from_bin(keyset.curve, blob.root_Q_compressed);
  if (rv) return rv;
  return keyset.root.K.from_bin(keyset.curve, blob.root_K_compressed);
}
```

**File:** src/cbmpc/api/hd_keyset_eddsa_2p.cpp (L143-152)
```cpp
error_t derive_eddsa_2p_keys(const coinbase::api::job_2p_t& job, mem_t keyset_blob, const bip32_path_t& hardened_path,
                             const std::vector<bip32_path_t>& non_hardened_paths, buf_t& sid,
                             std::vector<buf_t>& out_eddsa_2p_key_blobs) {
  if (const error_t rv = validate_job_2p(job)) return rv;
  if (const error_t rv = coinbase::api::detail::validate_mem_arg_max_size(keyset_blob, "keyset_blob",
                                                                          coinbase::api::detail::MAX_OPAQUE_BLOB_SIZE))
    return rv;
  coinbase::mpc::key_share_eddsa_hdmpc_2p_t keyset;
  error_t rv = deserialize_keyset_blob(keyset_blob, keyset);
  if (rv) return rv;
```

**File:** src/cbmpc/api/hd_keyset_eddsa_2p.cpp (L176-187)
```cpp
  std::vector<buf_t> blobs;
  blobs.resize(derived_keys.size());
  for (size_t i = 0; i < derived_keys.size(); i++) {
    rv = serialize_eddsa2pc_key_blob(derived_keys[i], blobs[i]);
    if (rv) {
      out_eddsa_2p_key_blobs.clear();
      return rv;
    }
  }

  out_eddsa_2p_key_blobs = std::move(blobs);
  return SUCCESS;
```

**File:** src/cbmpc/api/ecdsa_mp.cpp (L176-179)
```cpp
  const auto& G = curve.generator();
  const auto it_self = Qis.find(blob.party_name);
  if (it_self == Qis.end()) return coinbase::error(E_FORMAT, "invalid key blob");
  if (blob.x_share * G != it_self->second) return coinbase::error(E_FORMAT, "invalid key blob");
```

**File:** src/cbmpc/protocol/hd_keyset_eddsa_2p.cpp (L105-163)
```cpp
  bn_t x_share = key.root.x_share;
  bn_t k_share = key.root.k_share;
  ecc_point_t K_share = key.root.get_K_share();
  ecc_point_t other_K_share = key.root.get_other_K_share();
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
  ecc_point_t Z = CBMPC_EVAL_VARTIME(Z1 + Z2);
  // The rest of Hard-Derive-2P
  buf_t y = crypto::ro::hash_string(Z).bitlen(bytes_to_bits(delta_size) + 256);
  bn_t delta = bn_t::from_bin(y.take(delta_size)) % q;
  buf_t chain_code = y.skip(delta_size);

  int n_hd_paths = (int)non_hardened_paths.size();
  derived_keys.resize(n_hd_paths);

  ecc_point_t delta_G = CBMPC_EVAL_VARTIME(delta * G);
  ecc_point_t Q_derived = CBMPC_EVAL_VARTIME(Q + delta_G);
  std::vector<bn_t> non_hard_delta = non_hard_derive(Q_derived, chain_code, non_hardened_paths);
  std::vector<bn_t> derived_xs(n_hd_paths);
  std::vector<ecc_point_t> derived_Qs(n_hd_paths);

  // Start of the difference with the ecdsa-2pc version.
  for (int i = 0; i < n_hd_paths; i++) {
    derived_keys[i].role = party_t(key.party_index);
    derived_keys[i].curve = curve;
    ecc_point_t non_hard_delta_G = CBMPC_EVAL_VARTIME(non_hard_delta[i] * G);
    derived_keys[i].Q = Q_derived + non_hard_delta_G;
    if (job.get_party() == party_t::p1)
      MODULO(q) derived_keys[i].x_share = x_share + delta + non_hard_delta[i];
    else
      derived_keys[i].x_share = x_share;
```
