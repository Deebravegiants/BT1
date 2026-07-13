I have traced the full code path. Let me summarize the findings.

**Call chain:** `deserialize_keyset_blob` → `blob_to_keyset` → `ecc_point_t::from_bin` → `ecurve_ed_t::from_bin` → `ec25519_core::from_bin`

**Key facts established:**

1. `blob_to_keyset` calls `from_bin` for both Q and K with no subsequent `curve.check()` or `is_in_subgroup()` call: [1](#0-0) 

2. `ec25519_core::from_bin` only validates that the point satisfies the curve equation (x² = (y²-1)/(dy²+1)). It does **not** check subgroup membership: [2](#0-1) 

3. The test suite explicitly confirms that `from_bin` succeeds for the order-2 torsion point (x=0, y=-1), `is_on_curve()` returns true, but `is_in_subgroup()` returns false and `curve.check()` fails: [3](#0-2) 

4. `is_in_subgroup()` for Ed25519 is a separate, non-trivial check (multiply by q-1 and compare): [4](#0-3) 

5. `ecurve_t::check()` calls `is_in_subgroup()` and would reject torsion points, but it is never called in `blob_to_keyset`: [5](#0-4) 

**Differential analysis — Q vs K torsion:**

For **K torsion**: `get_other_K_share()` = `K - k_share * G`. If K is a torsion point T, `other_K_share = T - k_share_1 * G ≠ k_share_2 * G`. The ZK DH proof verification in `derive_keys` would then fail when P1 verifies P2's proof, so the K torsion attack is caught at runtime: [6](#0-5) [7](#0-6) 

For **Q torsion**: Q is used directly in `derive_keys` with no ZK proof involving Q. The ZK DH proofs only cover the K/VRF computation. Q flows straight into `Q_derived = Q + delta_G` and then into all derived child key public keys: [8](#0-7) [9](#0-8) 

**Contrast with other API paths** that correctly call `curve.check()` and `is_in_subgroup()` after `from_bin`: [10](#0-9) [11](#0-10) 

---

### Title
Missing subgroup check on `root_Q_compressed` in HD-EdDSA-2P keyset blob deserialization allows torsion-point injection into all derived child key public keys — (`src/cbmpc/api/hd_keyset_eddsa_2p.cpp`)

### Summary
`blob_to_keyset` calls `ecc_point_t::from_bin` for `root_Q_compressed` but never calls `curve.check()` or `is_in_subgroup()` afterward. Ed25519's `from_bin` accepts any point on the curve, including the 8 low-order torsion points. A torsion Q propagates silently through `derive_keys`, contaminating every derived child key's public key with a torsion component, while the x-shares remain prime-order. The two parties end up with inconsistent derived keys.

### Finding Description
In `src/cbmpc/api/hd_keyset_eddsa_2p.cpp` lines 78–80, `blob_to_keyset` deserializes `root_Q_compressed` via `keyset.root.Q.from_bin(keyset.curve, blob.root_Q_compressed)` and returns immediately on error, but performs no subsequent subgroup check. `ec25519_core::from_bin` (lines 872–912) only solves x² = (y²-1)/(dy²+1) — it accepts any curve point, including the order-2 point (x=0, y=p-1). The test `CryptoEdDSA::RejectTorsionAndFixInfinityEq` explicitly documents that `from_bin` returns `SUCCESS` for this point while `is_in_subgroup()` returns false.

In `derive_keys` (lines 109, 148–159), Q is read directly from the keyset and used as `Q_derived = Q + delta * G`. No subgroup check is performed. If Q = T (a torsion point), then every derived child key's public key becomes `T + (delta + non_hard_delta_i) * G`, which is not in the prime-order subgroup. Because `non_hard_derive` is seeded from `Q_derived`, the two parties also compute different `non_hard_delta` values, making the derived keys mutually inconsistent.

The K torsion attack is separately mitigated: `get_other_K_share()` = `K - k_share * G`, so a torsion K causes the ZK DH proof verification to fail at runtime. The Q torsion attack has no analogous runtime guard.

### Impact Explanation
An attacker who can supply a crafted keyset blob (e.g., a compromised storage layer, a malicious party injecting their own blob, or a party tampering with their own persisted blob before passing it to `derive_eddsa_2p_keys`) can set `root_Q_compressed` to any of the 8 Ed25519 torsion points. All derived child key public keys will be torsion-contaminated. The two parties will derive inconsistent keys (different `non_hard_delta` values), so any subsequent signing will either fail or produce signatures that verify against the wrong public key. The `refresh` path also propagates the torsion Q unchanged (`new_key.root.Q = key.root.Q`), so the corruption persists across refreshes.

This fits **High** impact: attacker-controlled blob data is accepted under an invalid cryptographic assumption (prime-order subgroup membership), producing accepted invalid cryptographic output. It does not reach **Critical** because the attacker cannot recover the other party's x-share or produce a valid signature without the honest party's participation.

### Likelihood Explanation
The keyset blob is an opaque byte string persisted by the caller and passed back into `refresh` and `derive_eddsa_2p_keys`. Any party that can write to the blob storage (including the party itself, a compromised storage backend, or a Byzantine participant) can inject a torsion Q. The missing check is a single omission relative to the pattern used in `eddsa2pc.cpp` and `eddsa_mp.cpp`.

### Recommendation
After both `from_bin` calls in `blob_to_keyset`, add subgroup validation:

```cpp
error_t rv = keyset.root.Q.from_bin(keyset.curve, blob.root_Q_compressed);
if (rv) return rv;
if (rv = keyset.curve.check(keyset.root.Q)) return coinbase::error(E_FORMAT, "invalid root_Q");

rv = keyset.root.K.from_bin(keyset.curve, blob.root_K_compressed);
if (rv) return rv;
if (rv = keyset.curve.check(keyset.root.K)) return coinbase::error(E_FORMAT, "invalid root_K");
```

`ecurve_t::check` already calls `is_in_subgroup()` and rejects infinity, matching the pattern used in `eddsa2pc.cpp` lines 204 and `eddsa_mp.cpp` lines 242/248.

### Proof of Concept
```cpp
// Craft a keyset blob with root_Q = Ed25519 order-2 torsion point (x=0, y=p-1).
// Encoding: y = 2^255 - 19 - 1 = 2^255 - 20, little-endian, sign bit = 0.
uint8_t torsion_Q[32];
torsion_Q[0] = 0xec;
for (int i = 1; i < 31; i++) torsion_Q[i] = 0xff;
torsion_Q[31] = 0x7f;

// Build a minimal valid keyset_blob_v1_t with root_Q_compressed = torsion_Q,
// valid role=0, curve=ed25519, x_share and k_share in [0,q), and any valid root_K.
// ... (serialize using the same converter_t format) ...

coinbase::mpc::key_share_eddsa_hdmpc_2p_t keyset;
error_t rv = deserialize_keyset_blob(crafted_blob, keyset);
// Expected: rv != SUCCESS (torsion point rejected)
// Actual:   rv == SUCCESS (torsion point accepted)
ASSERT_NE(rv, SUCCESS);  // This assertion FAILS — demonstrating the bug.
```

### Citations

**File:** src/cbmpc/api/hd_keyset_eddsa_2p.cpp (L78-80)
```cpp
  error_t rv = keyset.root.Q.from_bin(keyset.curve, blob.root_Q_compressed);
  if (rv) return rv;
  return keyset.root.K.from_bin(keyset.curve, blob.root_K_compressed);
```

**File:** src/cbmpc/crypto/ec25519_core.cpp (L865-870)
```cpp
bool is_in_subgroup(const crypto::ecp_storage_t* a) {
  static bn_t q_minus_1 = bn_t::from_hex("1000000000000000000000000000000014DEF9DEA2F79CD65812631A5CF5D3EC");
  point_t x;
  curve_t::mul(*(const point_t*)a, q_minus_1, x);
  return *(const point_t*)a == -x;
}
```

**File:** src/cbmpc/crypto/ec25519_core.cpp (L872-912)
```cpp
static error_t from_bin(point_t& R, mem_t bin) {
  if (bin.size != 32) return coinbase::error(E_FORMAT);

  buf_t buf = bin.rev();
  uint8_t neg = buf[0] >> 7;
  buf[0] &= 0x7f;
  fe_t y = fe_t::to_fe(uint256_t::from_bin(buf));

  // x² = (y² - 1) / (dy² + 1)

  fe_t u, v, w, vxx, check;

  u = y * y;
  v = u * formula_t::get_d();
  u -= fe_t::one();       // u = y^2-1
  v += fe_t::one();       // v = dy^2+1
  w = u * v;              // w = u*v
  fe_t x = w.pow22523();  // x = w^((q-5)/8)
  x *= u;                 // x = u * w^((q-5)/8)

  vxx = x * x;
  vxx *= v;
  check = vxx - u;  // vx^2-u
  if (!check.is_zero()) {
    check = vxx + u;  // vx^2+u
    if (!check.is_zero()) {
      return coinbase::error(E_CRYPTO);
    }
    static const fe_t sqrtm1 =
        fe_t::from_bn(bn_t::from_hex("2b8324804fc1df0b2b4d00993dfbd7a72f431806ad2fe478c4ee1b274a0ea0b0"));
    x *= sqrtm1;
  }

  uint256_t x_val = x.from_fe();
  if (neg != (x_val.w0 & 1)) x = -x;

  R.x = x;
  R.y = y;
  R.z = fe_t::one();
  return 0;
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

**File:** include-internal/cbmpc/internal/protocol/hd_tree_bip32.h (L11-12)
```text
  ecc_point_t get_K_share() const { return K.get_curve().mul_to_generator(k_share); }
  ecc_point_t get_other_K_share() const { return K - get_K_share(); }
```

**File:** src/cbmpc/protocol/hd_keyset_eddsa_2p.cpp (L109-109)
```cpp
  ecc_point_t Q = key.root.Q;
```

**File:** src/cbmpc/protocol/hd_keyset_eddsa_2p.cpp (L128-138)
```cpp
  if (job.is_p2()) {
    // Verification that Z1 is valid is done in the verify function
    if (rv = zk_dh1.verify(P, other_K_share, Z1, sid, 1)) return rv;
    zk_dh2.prove(P, K_share, Z2, k_share, sid, 2);
  }

  if (rv = job.p2_to_p1(Z2, zk_dh2)) return rv;

  if (job.is_p1()) {
    if (rv = zk_dh2.verify(P, other_K_share, Z2, sid, 2)) return rv;
  }
```

**File:** src/cbmpc/protocol/hd_keyset_eddsa_2p.cpp (L148-159)
```cpp
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

**File:** src/cbmpc/api/eddsa2pc.cpp (L202-205)
```cpp
  if (rv = Qi_self.from_bin(curve, public_share_compressed))
    return coinbase::error(rv, "invalid public_share_compressed");
  if (rv = curve.check(Qi_self)) return coinbase::error(rv, "invalid public_share_compressed");
  if (!Qi_self.is_in_subgroup()) return coinbase::error(E_FORMAT, "invalid public_share_compressed");
```

**File:** src/cbmpc/api/eddsa_mp.cpp (L241-248)
```cpp
  if (rv = Q.from_bin(curve, blob.Q_compressed)) return coinbase::error(rv, "invalid key blob");
  if (curve.check(Q)) return coinbase::error(E_FORMAT, "invalid key blob");

  coinbase::crypto::ss::party_map_t<coinbase::crypto::ecc_point_t> Qis;
  for (const auto& kv : blob.Qis_compressed) {
    coinbase::crypto::ecc_point_t Qi;
    if (rv = Qi.from_bin(curve, kv.second)) return coinbase::error(rv, "invalid key blob");
    if (!Qi.is_in_subgroup()) return coinbase::error(E_FORMAT, "invalid key blob");
```
