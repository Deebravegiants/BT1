The code is now fully traced. Let me confirm the exact call chain and the guard's effectiveness.

### Title
PVE Key Substitution via Attacker-Controlled `x_rows[i]` and `Q` When `skip_verify=true` — (`src/cbmpc/api/pve_base_pke.cpp`)

---

### Summary

`cbmpc_pve_decrypt` (and the C++ `coinbase::api::pve::decrypt` it delegates to) unconditionally passes `skip_verify=true` to `ec_pve_t::decrypt`, bypassing the ZK-proof consistency check. Both `x_rows[i]` and `Q` are fully attacker-controlled fields deserialized from the ciphertext blob. The only post-decryption guard — `x_value * G != Q` — is circular: because `Q` is also attacker-supplied, an attacker can trivially satisfy it for any chosen `x_target`, causing the decryptor to accept and return an attacker-chosen scalar as the recovered key.

---

### Finding Description

**Call chain:**

```
cbmpc_pve_decrypt (c_api/pve_base_pke.cpp:480)
  → coinbase::api::pve::decrypt (api/pve_base_pke.cpp:247)
      → pve_ct.decrypt(..., /*skip_verify=*/true)  (api/pve_base_pke.cpp:278-279)
          → ec_pve_t::decrypt (pve.cpp:147)
              line 150: verify() SKIPPED because skip_verify=true
              → restore_from_decrypted(i, x_buf, curve, x_out)  (pve.cpp:157)
                  line 132: x_bi = x_rows[row_index]  ← attacker-controlled
                  line 138: x_value = x_bi_bar + x_bi
                  line 140: if (x_value * G != Q) → Q is also attacker-controlled
```

**Deserialization makes all fields attacker-controlled:**

The `ec_pve_t::convert` method (pve.h:24-31) deserializes `Q`, `b`, `x_rows[i]`, `r[i]`, and `c[i]` directly from the ciphertext blob with no independent validation. Every field the attack depends on is attacker-supplied.

**Why `verify()` would block this but is skipped:**

`ec_pve_t::verify` (pve.cpp:70-116) re-encrypts `x_rows[i]` under `ek` and checks the result matches `c[i]`. An attacker who sets `c[i]` = Enc(`ek`, `inner_label`, 0) but `x_rows[i]` = `x_target` would fail this check because re-encrypting `x_target` produces a different ciphertext. With `skip_verify=true` this entire check is never reached.

**Why the post-decryption guard is insufficient:**

The guard at pve.cpp:140 checks `x_value * G == Q`. But `Q` is read from the same attacker-controlled blob (pve.h:35). The attacker sets `Q = x_target * G`, so the check is a tautology for any `x_target` they choose.

---

### Impact Explanation

An attacker who can supply a crafted ciphertext blob to `cbmpc_pve_decrypt` can make the decryptor recover any scalar `x_target` of the attacker's choosing, with a matching `Q = x_target * G`. The decryptor has no way to distinguish this from a legitimately encrypted key. Because the attacker chose `x_target`, they know the private key the decryptor will use going forward — enabling full impersonation, signature forgery, or key-share substitution depending on how the recovered scalar is consumed.

This fits the **High** impact category: "Attacker-controlled ciphertexts are accepted under the wrong key," and potentially **Critical** if the recovered scalar feeds directly into a signing or key-derivation path.

---

### Likelihood Explanation

The attack requires only:
1. The ability to supply a ciphertext blob to `cbmpc_pve_decrypt` — the normal API use case.
2. Knowledge of the public `ek` (needed to encrypt `0` under it) — `ek` is a public key by definition.
3. Knowledge of the `label` — a public associated-data value.

No threshold collusion, no secret material, and no side-channel access is required. The crafted ciphertext is a straightforward construction.

---

### Recommendation

Remove `skip_verify=true` from `coinbase::api::pve::decrypt` (api/pve_base_pke.cpp:278-279) so that `ec_pve_t::verify` is always called before decryption at the public API layer. The `skip_verify` parameter should remain available only for internal callers that have already verified the ciphertext through a separate, authenticated channel (e.g., the MPC protocol layer where the ciphertext was produced by a verified peer). The current API-level documentation comment ("designed to not leak secret information") is misleading — the real risk is not leakage but substitution.

---

### Proof of Concept

```
Given: legitimate (ek, dk) keypair, curve C, label L, target scalar x_target

1. Compute Q_fake = x_target * G

2. Compute inner_label = genPVELabelWithPoint(L, Q_fake)
   // same function used internally; Q is public in the ciphertext

3. Encrypt 0 under ek with inner_label:
   c_attack = base_pke.encrypt(ek, inner_label, 0, rho)

4. Choose any row index i, set b such that bit i = 1

5. Build ec_pve_t blob:
   Q       = Q_fake
   L       = L
   b       = (bit i = 1, rest = 0)
   x_rows[i] = x_target   // attacker-controlled field
   r[i]    = any 128-bit value
   c[i]    = c_attack

6. Serialize into pve_ciphertext_blob_v1_t and call cbmpc_pve_decrypt(dk, ek, crafted_ct, L)

Expected result:
  base_pke.decrypt(dk, inner_label, c_attack) → 0  (x_bi_bar)
  x_bi = x_rows[i] = x_target
  x_value = 0 + x_target = x_target
  x_target * G == Q_fake  → check passes
  cbmpc_pve_decrypt returns x_target  ← attacker-chosen key accepted
```

The assertion `x_out * G == Q_from_ciphertext` will pass, but `Q_from_ciphertext` was set by the attacker, not by the legitimate encryptor.

---

**Relevant code locations:**

`coinbase::api::pve::decrypt` unconditionally passes `skip_verify=true`: [1](#0-0) 

`ec_pve_t::decrypt` skips `verify()` when `skip_verify=true`: [2](#0-1) 

`restore_from_decrypted` reads `x_rows[row_index]` from the deserialized ciphertext without independent validation: [3](#0-2) 

The post-decryption guard checks against `Q`, which is also attacker-controlled: [4](#0-3) 

Both `Q` and `x_rows[i]` are deserialized directly from the attacker-supplied blob: [5](#0-4)

### Citations

**File:** src/cbmpc/api/pve_base_pke.cpp (L277-279)
```cpp
  coinbase::crypto::bn_t x_bn;
  rv = pve_ct.decrypt(bridge, coinbase::mpc::pve_keyref(dk_mem), coinbase::mpc::pve_keyref(ek_mem), label, icurve, x_bn,
                      /*skip_verify=*/true);
```

**File:** src/cbmpc/protocol/pve.cpp (L129-132)
```cpp
  if (bi) {
    if (x_rows[row_index].get_bin_size() > max_scalar_size) return coinbase::error(E_CRYPTO);
    if (!q.is_in_range(x_rows[row_index])) return coinbase::error(E_CRYPTO);
    x_bi = x_rows[row_index];
```

**File:** src/cbmpc/protocol/pve.cpp (L140-143)
```cpp
  if (x_value * G != Q) {
    x_value = 0;
    return coinbase::error(E_CRYPTO);
  }
```

**File:** src/cbmpc/protocol/pve.cpp (L148-150)
```cpp
                          bn_t& x_out, bool skip_verify) const {
  error_t rv = UNINITIALIZED_ERROR;
  if (!skip_verify && (rv = verify(base_pke, ek, Q, label))) return rv;
```

**File:** include-internal/cbmpc/internal/protocol/pve.h (L24-31)
```text
  void convert(coinbase::converter_t& converter) {
    converter.convert(Q, L, b);
    for (int i = 0; i < kappa; i++) {
      converter.convert(x_rows[i]);
      converter.convert(r[i]);
      converter.convert(c[i]);
    }
  }
```
