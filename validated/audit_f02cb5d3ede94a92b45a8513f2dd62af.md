The key question is whether `blob_to_keyset` in `hd_keyset_eddsa_2p.cpp` validates `root_Q` as a prime-order subgroup point. Let me confirm the exact code path.

The missing guard is confirmed. Here is the complete analysis:

**Key facts established:**

1. `blob_to_keyset` in `hd_keyset_eddsa_2p.cpp` calls `from_bin` on `root_Q` (line 78) but never calls `curve.check()` or `is_in_subgroup()` afterward. [1](#0-0) 

2. `ecurve_ed_t::from_bin` only checks that the point satisfies the curve equation — it does **not** check subgroup membership. The test suite explicitly confirms that `from_bin` succeeds for the order-2 torsion point (x=0, y=-1) and that `is_in_subgroup()` returns false for it. [2](#0-1) 

3. `ecurve_t::check()` calls `is_in_subgroup()` and would reject torsion points — but it is never called on `root_Q` in `blob_to_keyset`. [3](#0-2) 

4. The analogous `deserialize_key_blob` in `eddsa_mp.cpp` **does** have the correct guard: `from_bin` followed immediately by `curve.check(Q)`. [4](#0-3) 

5. `extract_root_public_key_compressed` calls `deserialize_keyset_blob` → `blob_to_keyset` and returns `keyset.root.Q.to_compressed_bin()` with no further validation. [5](#0-4) 

---

### Title
Missing prime-order subgroup check on `root_Q` in `blob_to_keyset` allows `extract_root_public_key_compressed` to return a torsion point as the Ed25519 root public key — (`src/cbmpc/api/hd_keyset_eddsa_2p.cpp`)

### Summary
`blob_to_keyset` in `hd_keyset_eddsa_2p.cpp` decodes `root_Q` via `from_bin` but omits the `curve.check()` call that every analogous deserializer in the codebase performs. An attacker who supplies a crafted keyset blob with `root_Q` set to an Ed25519 torsion point (on-curve but not in the prime-order subgroup) can cause `extract_root_public_key_compressed` to return a 32-byte encoding of that torsion point as the "root public key" without any error.

### Finding Description
`blob_to_keyset` (`src/cbmpc/api/hd_keyset_eddsa_2p.cpp`, lines 63–81) deserializes the HD keyset blob. After decoding `root_Q` with `from_bin`, it performs no subgroup check:

```cpp
error_t rv = keyset.root.Q.from_bin(keyset.curve, blob.root_Q_compressed);
if (rv) return rv;
return keyset.root.K.from_bin(keyset.curve, blob.root_K_compressed);
```

`ecurve_ed_t::from_bin` only verifies that the point satisfies the Edwards curve equation — it explicitly does **not** check subgroup membership. The cofactor of Ed25519 is 8, so there are 8 torsion cosets; a torsion point (e.g., the order-2 point with y = p−1) passes `from_bin` successfully.

`ecurve_t::check()` is the correct guard: it calls `is_in_subgroup()`, which for Ed25519 multiplies by q−1 and checks the result equals the negation of the input. This guard is present in every analogous deserializer (`eddsa_mp.cpp` line 137, `eddsa2pc.cpp` line 204/216) but is absent here.

`extract_root_public_key_compressed` (lines 190–199) is a public, single-party API (no job/transport required) that calls `deserialize_keyset_blob` → `blob_to_keyset` and immediately returns `keyset.root.Q.to_compressed_bin()`. The same missing guard also affects `refresh` and `derive_eddsa_2p_keys`, which both call `deserialize_keyset_blob`.

### Impact Explanation
A caller that passes the returned 32-byte value to any standard Ed25519 verifier as the public key will hold a torsion point. Torsion points are on the curve but not in the prime-order subgroup, so any signature produced against a legitimately derived key will fail external Ed25519 verification when the verifier uses the torsion root public key. Additionally, if `derive_eddsa_2p_keys` is called with a blob containing a torsion `root_Q`, the derivation protocol operates on a torsion root, potentially producing derived public keys that are also outside the prime-order subgroup, causing all downstream signing and verification to fail or produce cryptographically invalid output. This falls squarely under the "High" impact category: attacker-controlled blob data is accepted without the required subgroup validation, producing invalid cryptographic output.

### Likelihood Explanation
The API `extract_root_public_key_compressed` accepts a single `mem_t keyset_blob` argument with no authentication or job context. Any caller (or any party that can supply a blob) can trigger this path. Crafting a valid-format keyset blob with a torsion `root_Q` requires only knowledge of the serialization format (`keyset_blob_v1_t`) and a known torsion point encoding — both are trivially available from the public header and the test suite. No threshold collusion or secret material is needed.

### Recommendation
Add `curve.check()` on both `root_Q` and `root_K` immediately after their respective `from_bin` calls in `blob_to_keyset`, mirroring the pattern used in `deserialize_key_blob` in `eddsa_mp.cpp`:

```cpp
error_t rv = keyset.root.Q.from_bin(keyset.curve, blob.root_Q_compressed);
if (rv) return rv;
if (keyset.curve.check(keyset.root.Q)) return coinbase::error(E_FORMAT, "invalid keyset blob");

rv = keyset.root.K.from_bin(keyset.curve, blob.root_K_compressed);
if (rv) return rv;
if (keyset.curve.check(keyset.root.K)) return coinbase::error(E_FORMAT, "invalid keyset blob");
```

### Proof of Concept
1. Construct a `keyset_blob_v1_t` with `version=1`, `curve=ed25519`, valid `role`, valid `x_share`/`k_share` in range, `root_K_compressed` = any valid Ed25519 point, and `root_Q_compressed` = the 32-byte encoding of the order-2 torsion point: `{0xec, 0xff, ...(29 bytes of 0xff)..., 0x7f}` (y = p−1, sign bit = 0).
2. Serialize this struct via the library's converter and pass it to `extract_root_public_key_compressed`.
3. The call returns `SUCCESS` and `out_Q_compressed` contains the 32-byte torsion point encoding.
4. Decode the returned bytes with any Ed25519 library: the point is on the curve but `is_in_subgroup()` returns false, confirming a torsion point was accepted and returned as the root public key.
5. Pass this torsion point as the public key to any standard Ed25519 verifier alongside a signature produced by `eddsa_2p::sign` on a legitimately derived key — verification fails.

### Citations

**File:** src/cbmpc/api/hd_keyset_eddsa_2p.cpp (L78-80)
```cpp
  error_t rv = keyset.root.Q.from_bin(keyset.curve, blob.root_Q_compressed);
  if (rv) return rv;
  return keyset.root.K.from_bin(keyset.curve, blob.root_K_compressed);
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

**File:** tests/unit/crypto/test_eddsa.cpp (L25-30)
```cpp
  ecc_point_t P(curve);
  EXPECT_EQ(P.from_bin(curve, mem_t(order2, 32)), SUCCESS);
  EXPECT_TRUE(P.is_on_curve());
  EXPECT_FALSE(P.is_infinity());
  EXPECT_FALSE(P.is_in_subgroup());
  EXPECT_NE(curve.check(P), SUCCESS);
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

**File:** src/cbmpc/api/eddsa_mp.cpp (L135-137)
```cpp
  coinbase::crypto::ecc_point_t Q;
  if (rv = Q.from_bin(curve, blob.Q_compressed)) return coinbase::error(rv, "invalid key blob");
  if (curve.check(Q)) return coinbase::error(E_FORMAT, "invalid key blob");
```
