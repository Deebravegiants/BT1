The code evidence is conclusive. Here is the analysis:

---

### Title
`allow_ecc_infinity_t` Guard Misplacement Allows Infinity-Point Share to Bypass Input Validation in `ac_t::reconstruct_exponent`, Producing Wrong Public Key — (`src/cbmpc/crypto/secret_sharing.cpp`)

### Summary

`ac_t::reconstruct_exponent` creates an `allow_ecc_infinity_t` RAII guard **before** the input-validation loop that calls `curve.check()` on each share. This guard disables the infinity-point rejection inside `curve.check()`. For Ed25519 (where `is_in_subgroup(infinity) == true`), a Byzantine peer can supply the point at infinity as a leaf public share; it passes all validation, reaches `lagrange_interpolate_exponent`, and causes a silently wrong reconstructed public key to be returned as `SUCCESS`.

### Finding Description

**Guard placement:**

```cpp
// src/cbmpc/crypto/secret_sharing.cpp:554-563
error_t ac_t::reconstruct_exponent(const ac_pub_shares_t& shares, ecc_point_t& P) const {
  if (!root) return coinbase::error(E_BADARG, "missing root");
  if (!curve.valid()) return coinbase::error(E_BADARG, "missing curve");
  allow_ecc_infinity_t allow_ecc_infinity;          // ← guard active from here
  for (const auto& [name, share] : shares) {
    error_t rv = curve.check(share);                // ← infinity check suppressed
    if (rv) return coinbase::error(rv, ...);
  }
  return reconstruct_exponent_recursive(root, shares, P);
}
``` [1](#0-0) 

**`allow_ecc_infinity_t` mechanism:**

```cpp
// src/cbmpc/crypto/base_ecc.cpp:587-600
static thread_local int thread_local_store_allow_ecc_infinity = 0;
allow_ecc_infinity_t::allow_ecc_infinity_t() { thread_local_store_allow_ecc_infinity++; }
allow_ecc_infinity_t::~allow_ecc_infinity_t() { thread_local_store_allow_ecc_infinity--; }

error_t ecurve_t::check(const ecc_point_t& point) const {
  ...
  if (!point.is_in_subgroup()) return crypto::error("EC-point is not on curve");
  if (!thread_local_store_allow_ecc_infinity) {     // ← bypassed when guard is active
    if (point.is_infinity()) return crypto::error("EC-point is infinity");
  }
  return SUCCESS;
}
``` [2](#0-1) 

**Ed25519 infinity is in subgroup (confirmed by test):**

```cpp
// tests/unit/crypto/test_eddsa.cpp:187-190
EXPECT_TRUE(I.is_infinity());
EXPECT_TRUE(I.is_in_subgroup());   // ← passes is_in_subgroup check
// By default, curve.check() rejects infinity unless allow_ecc_infinity_t is in scope.
EXPECT_NE(curve.check(I), SUCCESS);
``` [3](#0-2) 

Because `is_in_subgroup(infinity) == true` for Ed25519, the only guard against infinity is the `thread_local_store_allow_ecc_infinity` check — which is already suppressed by the misplaced guard. The infinity share passes `curve.check()` and enters `reconstruct_exponent_recursive`.

**THRESHOLD node path:**

```cpp
// src/cbmpc/crypto/secret_sharing.cpp:518-543
case node_e::THRESHOLD: {
  ...
  node_shares[count] = Pi;   // Pi may be the infinity point
  ...
  P = lagrange_interpolate_exponent(0, node_shares, pids);
}
``` [4](#0-3) 

**Inside `lagrange_interpolate_exponent` → `lagrange_partial_interpolate_exponent`:**

```cpp
// src/cbmpc/crypto/lagrange.cpp:123-126
for (int i = 0; i < m; i++) {
  bn_t lambda = lagrange_basis(x, all_pids, pids_for_shares[i], q);
  R += lambda * shares[i];   // lambda * infinity = infinity; R += infinity is a no-op
}
``` [5](#0-4) 

`lambda * infinity = infinity` (scalar multiplication of the identity is always the identity). Adding infinity to `R` is a no-op. The contribution of the Byzantine share is silently dropped, and `lagrange_interpolate_exponent` returns a wrong point — the interpolation of the remaining shares only, evaluated at `x=0`. The function returns `SUCCESS` with no error.

**secp256k1 is NOT affected** because `ecurve_secp256k1_t::is_in_subgroup()` calls `secp256k1_ge_is_valid_var()` on the affine representation, which returns `0` for the infinity point (infinity is not a valid affine point). So `curve.check(infinity)` fails at the `is_in_subgroup` check regardless of the guard. [6](#0-5) 

### Impact Explanation

A Byzantine participant in a threshold access-structure protocol using Ed25519 can submit the point at infinity as their public share. `ac_t::reconstruct_exponent` accepts it, computes a wrong group public key, and returns `SUCCESS`. Any downstream protocol step that trusts the reconstructed public key (e.g., verifying a threshold signature, deriving a shared key, or comparing against a committed value) will operate on the wrong key. This constitutes accepted invalid cryptographic output with security impact: honest parties diverge on the group public key, and signature verification will fail or the wrong key will be used for subsequent operations.

### Likelihood Explanation

The attacker only needs to be a single Byzantine participant below threshold — they provide their own public share as the infinity point. No collusion is required. The `allow_ecc_infinity_t` guard is a thread-local RAII object; there is no race condition or environment dependency. The bug is deterministically triggered on any Ed25519 access structure with a THRESHOLD node whenever one share is the infinity point.

### Recommendation

Move the `allow_ecc_infinity_t allow_ecc_infinity;` declaration to **after** the input-validation loop, so that `curve.check()` runs with the default (infinity-rejecting) behavior for all caller-supplied shares:

```cpp
error_t ac_t::reconstruct_exponent(const ac_pub_shares_t& shares, ecc_point_t& P) const {
  if (!root) return coinbase::error(E_BADARG, "missing root");
  if (!curve.valid()) return coinbase::error(E_BADARG, "missing curve");
  // Validate inputs BEFORE allowing infinity in intermediate computations
  for (const auto& [name, share] : shares) {
    error_t rv = curve.check(share);
    if (rv) return coinbase::error(rv, "invalid share point for " + name);
  }
  allow_ecc_infinity_t allow_ecc_infinity;  // only needed for intermediate results
  return reconstruct_exponent_recursive(root, shares, P);
}
```

Alternatively, add an explicit `is_infinity()` check inside the validation loop that is unconditional (independent of the guard).

### Proof of Concept

```cpp
// Ed25519, 2-of-3 threshold node with leaves at pids {1,2,3}
ecurve_t curve = curve_ed25519;
const mod_t q = curve.order();
const bn_t x = bn_t::rand(q);
ac_t ac(threshold_2_of_3_root, curve);

// Honest shares
const ac_shares_t shares = ac.share(q, x, nullptr);
ac_pub_shares_t pub_shares;
for (const auto& [name, si] : shares)
  pub_shares[name] = si * curve.generator();

// Byzantine: replace leaf1's share with the infinity point
pub_shares["leaf1"] = curve.infinity();

ecc_point_t P;
// This returns SUCCESS — wrong!
error_t rv = ac.reconstruct_exponent(pub_shares, P);
assert(rv == SUCCESS);

// P != x * curve.generator() — wrong public key accepted
ecc_point_t correct = x * curve.generator();
assert(P != correct);  // passes: wrong key was silently accepted
```

### Citations

**File:** src/cbmpc/crypto/secret_sharing.cpp (L518-544)
```cpp
    case node_e::THRESHOLD: {
      std::vector<bn_t> pids(node->threshold);
      std::vector<ecc_point_t> node_shares(node->threshold);
      int count = 0;

      for (int i = 0; i < n; i++) {
        ecc_point_t Pi;
        rv = reconstruct_exponent_recursive(node->children[i], shares, Pi);
        if (rv == E_INSUFFICIENT) {
          rv = SUCCESS;
          continue;
        }
        if (rv) return coinbase::error(rv, "cannot reconstruct threshold node " + name);

        pids[count] = node->children[i]->get_pid();
        node_shares[count] = Pi;
        count++;
        if (count == node->threshold) break;
      }

      if (count < node->threshold) {
        dylog_disable_scope_t dylog_disable_scope;
        return coinbase::error(E_INSUFFICIENT, "missing share for threshold node " + name);
      }

      P = lagrange_interpolate_exponent(0, node_shares, pids);
    } break;
```

**File:** src/cbmpc/crypto/secret_sharing.cpp (L554-564)
```cpp
error_t ac_t::reconstruct_exponent(const ac_pub_shares_t& shares, ecc_point_t& P) const {
  if (!root) return coinbase::error(E_BADARG, "missing root");
  if (!curve.valid()) return coinbase::error(E_BADARG, "missing curve");
  allow_ecc_infinity_t allow_ecc_infinity;
  for (const auto& [name, share] : shares) {
    error_t rv = curve.check(share);
    if (rv) return coinbase::error(rv, "invalid share point for " + name);
  }

  return reconstruct_exponent_recursive(root, shares, P);
}
```

**File:** src/cbmpc/crypto/base_ecc.cpp (L587-601)
```cpp
static thread_local int thread_local_store_allow_ecc_infinity = 0;

allow_ecc_infinity_t::allow_ecc_infinity_t() { thread_local_store_allow_ecc_infinity++; }
allow_ecc_infinity_t::~allow_ecc_infinity_t() { thread_local_store_allow_ecc_infinity--; }

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

**File:** tests/unit/crypto/test_eddsa.cpp (L187-190)
```cpp
  EXPECT_TRUE(I.is_infinity());
  EXPECT_TRUE(I.is_in_subgroup());
  // By default, curve.check() rejects infinity unless allow_ecc_infinity_t is in scope.
  EXPECT_NE(curve.check(I), SUCCESS);
```

**File:** src/cbmpc/crypto/lagrange.cpp (L123-126)
```cpp
  for (int i = 0; i < m; i++) {
    bn_t lambda = lagrange_basis(x, all_pids, pids_for_shares[i], q);
    R += lambda * shares[i];
  }
```

**File:** src/cbmpc/crypto/base_ecc_secp256k1.cpp (L127-132)
```cpp
bool ecurve_secp256k1_t::is_on_curve(const ecc_point_t& P) const {
  secp256k1_ge ge = secp256k1_gej_to_ge((const secp256k1_gej*)P.secp256k1);
  return 0 != secp256k1_ge_is_valid_var(&ge);
}

bool ecurve_secp256k1_t::is_in_subgroup(const ecc_point_t& P) const { return is_on_curve(P); }
```
