### Title
AND-Node Additive-Share Accumulation Uses Assignment Instead of Addition in `to_additive_share` — (File: src/cbmpc/protocol/ec_dkg.cpp)

### Summary
`key_share_mp_t::reconstruct_additive_share` and `key_share_mp_t::reconstruct_pub_additive_shares` both handle the `AND` node case with a plain assignment (`=`) instead of modular accumulation (`+=`). When a signing party appears in more than one branch of an AND node, only the last non-zero child's contribution is retained. The resulting additive key share is arithmetically wrong, so the combined ECDSA/Schnorr signature produced by `sign_ac` is invalid.

### Finding Description

In `reconstruct_additive_share`, the `AND` case iterates over all children and writes:

```cpp
if (additive_share_from_child != 0) {
    additive_share = additive_share_from_child;   // ← overwrites, not accumulates
}
``` [1](#0-0) 

The correct AND secret-sharing reconstruction requires summing every child's contribution, exactly as the sibling function `reconstruct_recursive` does:

```cpp
MODULO(q) x += share;   // correct accumulation
``` [2](#0-1) 

The same overwrite bug appears in the public-share counterpart:

```cpp
if (!additive_share_from_child.is_infinity()) {
    pub_additive_shares = additive_share_from_child;  // ← overwrites
}
``` [3](#0-2) 

Both functions are called unconditionally from `to_additive_share`: [4](#0-3) 

`to_additive_share` is the sole conversion step before every AC-based signing call. For ECDSA:

```cpp
rv = ac_key.to_additive_share(ac, quorum_names, additive_key);
...
return coinbase::mpc::ecdsampc::sign(mpc_job, additive_key, msg, sig_receiver, sig_der);
``` [5](#0-4) 

And for Schnorr/BIP340: [6](#0-5) 

### Impact Explanation

In AND secret sharing the dealer splits the secret as `x = x₁ + x₂ + … + xₙ (mod q)` and distributes each `xᵢ` independently through child `i`. A party `P` that participates in two or more AND branches holds a non-zero share from each branch. Its correct additive contribution is the sum of all those Lagrange-weighted shares. Because the loop overwrites instead of accumulates, `P`'s `x_share` in the resulting `additive_key` equals only the last branch's contribution. The sum of all parties' additive shares therefore does not equal the actual private key `x`, so every call to `sign_ac` with such an access structure produces a cryptographically invalid signature — a public-API-reachable quorum-invariant break that causes honest-party divergence and invalid cryptographic output.

Because `reconstruct_pub_additive_shares` carries the identical overwrite bug, the `Qis` map is also wrong in the same way. The internal self-consistency check `x_share * G == Qi[self]` still passes (both sides are wrong identically), so no early error is raised and the bad state silently propagates into the signing round.

### Likelihood Explanation

Any caller that constructs an AND-rooted access structure where at least one leaf party name appears under two or more AND branches (e.g., `AND(threshold(P,Q,R), threshold(P,S,T))`) will trigger the bug on every `sign_ac` / `sign_ac` invocation. The public API accepts arbitrary `access_structure_t` inputs with no documented restriction against repeated leaf names across AND branches, and no runtime validation rejects such structures before `to_additive_share` is called.

### Recommendation

Replace the plain assignment with modular accumulation in both functions:

**`reconstruct_additive_share`, AND case:**
```cpp
// Before (line 525):
additive_share = additive_share_from_child;
// After:
MODULO(q) additive_share += additive_share_from_child;
```

**`reconstruct_pub_additive_shares`, AND case:**
```cpp
// Before (line 635):
pub_additive_shares = additive_share_from_child;
// After:
pub_additive_shares += additive_share_from_child;
```

Add a unit test with an AND access structure where one party appears in multiple branches and verify that the reconstructed additive shares sum to the original secret.

### Proof of Concept

Consider three parties `P`, `Q`, `R` and the access structure `AND(threshold_2(P,Q,R), threshold_2(P,Q,R))` (party `P` appears in both AND branches).

1. Run `dkg_ac` / `dkg_or_refresh_ac` to generate key shares under this structure. Each party receives a share of `x₁` (branch 1) and a share of `x₂` (branch 2), where `x = x₁ + x₂ mod q`.

2. Party `P` calls `sign_ac`. Inside `to_additive_share → reconstruct_additive_share`:
   - Branch 1 returns `λ₁ · s_P1 ≠ 0` → `additive_share = λ₁ · s_P1`
   - Branch 2 returns `λ₂ · s_P2 ≠ 0` → `additive_share = λ₂ · s_P2` (overwrites)
   - Correct value should be `λ₁ · s_P1 + λ₂ · s_P2`

3. The signing protocol runs with `P`'s wrong additive share. The combined signature `(r, s)` satisfies `s = k⁻¹(m + r · x') mod q` where `x' ≠ x`, so `r ≠ x·G_x` and the ECDSA verification equation fails.

4. All honest parties observe an invalid signature despite completing the protocol without error, confirming the invariant break.

### Citations

**File:** src/cbmpc/protocol/ec_dkg.cpp (L524-526)
```cpp
        if (additive_share_from_child != 0) {
          additive_share = additive_share_from_child;
        }
```

**File:** src/cbmpc/protocol/ec_dkg.cpp (L634-636)
```cpp
        if (!additive_share_from_child.is_infinity()) {
          pub_additive_shares = additive_share_from_child;
        }
```

**File:** src/cbmpc/protocol/ec_dkg.cpp (L695-724)
```cpp
error_t key_share_mp_t::to_additive_share(const crypto::ss::ac_t ac, const std::set<crypto::pname_t>& quorum_names,
                                          key_share_mp_t& additive_share) {
  if (!ac.enough_for_quorum(quorum_names)) {
    return coinbase::error(E_INSUFFICIENT);
  }
  error_t rv = UNINITIALIZED_ERROR;
  const mod_t& q = curve.order();
  bn_t new_x_share;
  bool _ignore_is_satisfied = false;
  if (rv = reconstruct_additive_share(q, ac.root, quorum_names, new_x_share, _ignore_is_satisfied)) return rv;

  party_map_t<ecc_point_t> new_Qis;
  std::vector<crypto::pname_t> quorum_names_vec(quorum_names.begin(), quorum_names.end());

  for (size_t j = 0; j < quorum_names_vec.size(); j++) {
    crypto::vartime_scope_t vartime_scope;
    bool _ignore_is_satisfied = false;
    ecc_point_t new_Qi;
    if (rv = reconstruct_pub_additive_shares(ac.root, quorum_names, quorum_names_vec[j], new_Qi, _ignore_is_satisfied))
      return rv;
    new_Qis[quorum_names_vec[j]] = new_Qi;
  }

  additive_share.x_share = new_x_share;
  additive_share.Q = Q;
  additive_share.Qis = new_Qis;
  additive_share.curve = curve;
  additive_share.party_name = party_name;

  return SUCCESS;
```

**File:** src/cbmpc/crypto/secret_sharing.cpp (L435-439)
```cpp
      for (int i = 0; i < n; i++) {
        bn_t share;
        if (rv = reconstruct_recursive(q, node->children[i], shares, share)) return rv;
        MODULO(q) x += share;
      }
```

**File:** src/cbmpc/api/ecdsa_mp.cpp (L428-435)
```cpp
  coinbase::mpc::ecdsampc::key_t additive_key;
  rv = ac_key.to_additive_share(ac, quorum_names, additive_key);
  if (rv) return rv;

  coinbase::mpc::job_mp_t mpc_job = to_internal_job(job);

  sig_der.free();
  return coinbase::mpc::ecdsampc::sign(mpc_job, additive_key, msg, sig_receiver, sig_der);
```

**File:** src/cbmpc/api/schnorr_mp.cpp (L396-404)
```cpp
  coinbase::mpc::schnorrmp::key_t additive_key;
  rv = ac_key.to_additive_share(ac, quorum_names, additive_key);
  if (rv) return rv;

  coinbase::mpc::job_mp_t mpc_job = to_internal_job(job);

  sig.free();
  return coinbase::mpc::schnorrmp::sign(mpc_job, additive_key, msg, sig_receiver, sig,
                                        coinbase::mpc::schnorrmp::variant_e::BIP340);
```
