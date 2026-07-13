Now I have enough information to make a determination. Let me verify the `curve.check()` implementation and the `from_bin` behavior for Ed25519 torsion points.

The vulnerability is real and concrete. Here is the complete analysis:

---

### Title
Missing Ed25519 Subgroup Check in `blob_to_keyset` Allows Torsion-Point Acceptance — (`src/cbmpc/api/hd_keyset_eddsa_2p.cpp`)

### Summary

`blob_to_keyset` in the EdDSA HD keyset API layer calls `from_bin` for `root_Q_compressed` and `root_K_compressed` but never calls `curve.check()` or `is_in_subgroup()` afterward. Because `from_bin` for Ed25519 accepts torsion points (confirmed by the codebase's own tests), a crafted keyset blob containing a known low-order point passes deserialization and propagates into `extract_root_public_key_compressed` (which returns `SUCCESS` with the torsion point as the public key) and into `derive_eddsa_2p_keys` (which returns `SUCCESS` with derived key blobs whose `Q` is not in the prime-order subgroup). The sibling function `eddsa2pc.cpp::blob_to_key` already applies the correct guard, making the omission in the HD keyset path a clear inconsistency.

### Finding Description

**The missing guard — `src/cbmpc/api/hd_keyset_eddsa_2p.cpp`, `blob_to_keyset`:**

```cpp
error_t rv = keyset.root.Q.from_bin(keyset.curve, blob.root_Q_compressed);
if (rv) return rv;
return keyset.root.K.from_bin(keyset.curve, blob.root_K_compressed);
// ← no curve.check(keyset.root.Q) or is_in_subgroup() here
``` [1](#0-0) 

**The correct guard — `src/cbmpc/api/eddsa2pc.cpp`, `blob_to_key`:**

```cpp
error_t rv = key.Q.from_bin(key.curve, blob.Q_compressed);
if (rv) return coinbase::error(rv, "invalid key blob");
if (key.curve.check(key.Q)) return coinbase::error(E_FORMAT, "invalid key blob");
``` [2](#0-1) 

**`from_bin` does NOT check subgroup membership.** `ecurve_ed_t::from_bin` delegates directly to `ec25519_core::from_bin` with no subgroup check: [3](#0-2) 

**`curve.check()` does check subgroup membership** via `is_in_subgroup()`: [4](#0-3) 

**The codebase's own tests confirm** that the known Ed25519 order-2 torsion point `{0xec, 0xff, ..., 0x7f}` passes `from_bin` with `SUCCESS`, returns `is_on_curve() == true`, `is_infinity() == false`, `is_in_subgroup() == false`, and `curve.check() != SUCCESS`: [5](#0-4) 

**Downstream propagation — `extract_root_public_key_compressed`:**

```cpp
const error_t rv = deserialize_keyset_blob(keyset_blob, keyset);
if (rv) return rv;
out_Q_compressed = keyset.root.Q.to_compressed_bin();  // returns torsion point
return SUCCESS;
``` [6](#0-5) 

**Downstream propagation — `derive_eddsa_2p_keys` → `derive_keys`:**

The torsion `Q` is loaded into `key.root.Q` and used directly:
```cpp
ecc_point_t Q = key.root.Q;                          // torsion point
ecc_point_t Q_derived = Q + delta_G;                 // torsion + subgroup ≠ subgroup
derived_keys[i].Q = Q_derived + non_hard_delta_G;    // still not in subgroup
``` [7](#0-6) 

`serialize_eddsa2pc_key_blob` then serializes the invalid `Q` without any check, and `derive_eddsa_2p_keys` returns `SUCCESS` with the invalid blob: [8](#0-7) 

### Impact Explanation

- `extract_root_public_key_compressed` returns `SUCCESS` and outputs a 32-byte encoding of a torsion point as the "root public key." Any downstream consumer (e.g., address derivation, key verification) that trusts this output receives a cryptographically invalid key without any error signal.
- `derive_eddsa_2p_keys` returns `SUCCESS` and outputs `eddsa_2p` key blobs whose embedded `Q` is not in the Ed25519 prime-order subgroup. These blobs are accepted as valid output of the derivation step. (They would be rejected later by `blob_to_key`'s `curve.check()` when used for signing, but the derivation step itself silently accepts and outputs them.)
- The `refresh` path also loads the tainted keyset and passes it to `key_share_eddsa_hdmpc_2p_t::refresh`, which copies `key.root.Q` and `key.root.K` directly into the new keyset without any check. [9](#0-8) 

### Likelihood Explanation

The attacker must supply a crafted `keyset_blob` to one of the three public API functions (`extract_root_public_key_compressed`, `derive_eddsa_2p_keys`, `refresh`). All three accept `mem_t keyset_blob` as a caller-supplied argument. The torsion point encoding is a fixed, publicly known 32-byte value. The blob format is documented (versioned, structured) and straightforward to craft. No protocol interaction is required for `extract_root_public_key_compressed`.

### Recommendation

In `blob_to_keyset` (`src/cbmpc/api/hd_keyset_eddsa_2p.cpp`), add `curve.check()` calls after each `from_bin`, mirroring the pattern already used in `blob_to_key` (`src/cbmpc/api/eddsa2pc.cpp`):

```cpp
error_t rv = keyset.root.Q.from_bin(keyset.curve, blob.root_Q_compressed);
if (rv) return rv;
if (keyset.curve.check(keyset.root.Q)) return coinbase::error(E_FORMAT, "invalid keyset blob");

rv = keyset.root.K.from_bin(keyset.curve, blob.root_K_compressed);
if (rv) return rv;
if (keyset.curve.check(keyset.root.K)) return coinbase::error(E_FORMAT, "invalid keyset blob");
```

### Proof of Concept

1. Construct a `keyset_blob_v1_t` with:
   - `version = 1`, `role = 0`, `curve = ed25519`
   - `root_Q_compressed = {0xec, 0xff, 0xff, ..., 0xff, 0x7f}` (32 bytes — known Ed25519 order-2 torsion point)
   - `root_K_compressed` = any valid Ed25519 point encoding
   - `x_share`, `k_share` = any values in `[0, q)`
2. Serialize via `coinbase::convert(blob)` to produce a `mem_t`.
3. Call `extract_root_public_key_compressed(crafted_blob, out_Q)` — observe it returns `SUCCESS` and `out_Q` encodes the torsion point.
4. Verify: decode `out_Q` with `ecc_point_t::from_bin`, assert `is_in_subgroup() == false`.
5. Call `derive_eddsa_2p_keys(job, crafted_blob, ...)` with a stub transport — observe it returns `SUCCESS` and the output blobs contain a `Q` that fails `curve.check()`.

### Citations

**File:** src/cbmpc/api/hd_keyset_eddsa_2p.cpp (L78-80)
```cpp
  error_t rv = keyset.root.Q.from_bin(keyset.curve, blob.root_Q_compressed);
  if (rv) return rv;
  return keyset.root.K.from_bin(keyset.curve, blob.root_K_compressed);
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

**File:** src/cbmpc/api/hd_keyset_eddsa_2p.cpp (L190-199)
```cpp
error_t extract_root_public_key_compressed(mem_t keyset_blob, buf_t& out_Q_compressed) {
  if (const error_t rv = coinbase::api::detail::validate_mem_arg_max_size(keyset_blob, "keyset_blob",
                                                                          coinbase::api::detail::MAX_OPAQUE_BLOB_SIZE))
    return rv;
  coinbase::mpc::key_share_eddsa_hdmpc_2p_t keyset;
  const error_t rv = deserialize_keyset_blob(keyset_blob, keyset);
  if (rv) return rv;
  out_Q_compressed = keyset.root.Q.to_compressed_bin();
  return SUCCESS;
}
```

**File:** src/cbmpc/api/eddsa2pc.cpp (L40-43)
```cpp
  error_t rv = key.Q.from_bin(key.curve, blob.Q_compressed);
  if (rv) return coinbase::error(rv, "invalid key blob");
  if (key.curve.check(key.Q)) return coinbase::error(E_FORMAT, "invalid key blob");
  return SUCCESS;
```

**File:** src/cbmpc/crypto/base_eddsa.cpp (L167-174)
```cpp
error_t ecurve_ed_t::from_bin(ecc_point_t& P, mem_t bin) const {
  error_t rv = ec25519_core::from_bin(P.storage, bin);
  if (rv != 0) {
    set_infinity(P);
    return rv;
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

**File:** tests/unit/crypto/test_eddsa.cpp (L14-37)
```cpp
TEST(CryptoEdDSA, RejectTorsionAndFixInfinityEq) {
  crypto::vartime_scope_t vartime_scope;
  ecurve_t curve = crypto::curve_ed25519;

  // Compressed encoding of the Ed25519 order-2 point (x=0, y=-1):
  // y = p-1 = 2^255-20, sign bit = 0.
  uint8_t order2[32];
  order2[0] = 0xec;
  for (int i = 1; i < 31; i++) order2[i] = 0xff;
  order2[31] = 0x7f;

  ecc_point_t P(curve);
  EXPECT_EQ(P.from_bin(curve, mem_t(order2, 32)), SUCCESS);
  EXPECT_TRUE(P.is_on_curve());
  EXPECT_FALSE(P.is_infinity());
  EXPECT_FALSE(P.is_in_subgroup());
  EXPECT_NE(curve.check(P), SUCCESS);

  // Sanity: infinity should not compare equal to the generator.
  const ecc_point_t G = curve.generator();
  const ecc_point_t I = curve.infinity();
  EXPECT_FALSE(G == I);
  EXPECT_TRUE(I.is_infinity());
}
```

**File:** src/cbmpc/protocol/hd_keyset_eddsa_2p.cpp (L61-62)
```cpp
  new_key.root.Q = key.root.Q;
  new_key.root.K = key.root.K;
```

**File:** src/cbmpc/protocol/hd_keyset_eddsa_2p.cpp (L109-159)
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
```
