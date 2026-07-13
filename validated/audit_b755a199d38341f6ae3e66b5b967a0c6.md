The code is clear. Let me verify the `restore_from_decrypted` check and the `genPVELabelWithPoint` function to complete the analysis.

### Title
PVE Cut-and-Choose Proof Unconditionally Skipped in All API-Layer Decrypt Paths - (`src/cbmpc/api/pve_base_pke.cpp`)

### Summary

Every public API decrypt entry point for PVE (`decrypt`, `decrypt_batch`, `combine_ac`) hard-codes `skip_verify=true` when calling the internal `ec_pve_t::decrypt`. The internal guard that runs the cut-and-choose proof (`ec_pve_t::verify`) is therefore never executed on the decryption path. The only surviving check is `x_value * G == Q` inside `restore_from_decrypted`, but `Q` is fully attacker-controlled as part of the serialized blob. An attacker who can supply the ciphertext blob can choose any scalar `x`, embed `Q = x*G`, craft a single syntactically valid row `c[i]` encrypted under the legitimate `ek`, and cause the honest decryptor to return `x` as the recovered private key — with the cut-and-choose proof never having been checked.

### Finding Description

**Entrypoint — API layer (`src/cbmpc/api/pve_base_pke.cpp` line 278):**

```cpp
rv = pve_ct.decrypt(bridge, coinbase::mpc::pve_keyref(dk_mem),
                    coinbase::mpc::pve_keyref(ek_mem), label, icurve, x_bn,
                    /*skip_verify=*/true);
```

The same pattern appears in `pve_batch_single_recipient.cpp` line 173 and `pve_batch_ac.cpp` line 354. All three API decrypt paths unconditionally pass `skip_verify=true`.

**Internal guard (`src/cbmpc/protocol/pve.cpp` line 150):**

```cpp
if (!skip_verify && (rv = verify(base_pke, ek, Q, label))) return rv;
```

When `skip_verify=true` this entire branch is dead. `verify()` — which reconstructs the commitment hash `b` and checks `b_tag == b`, checks `Q == this->Q`, and checks `label == L` — is never called.

**Remaining check (`src/cbmpc/protocol/pve.cpp` lines 140–143):**

```cpp
if (x_value * G != Q) {
    x_value = 0;
    return coinbase::error(E_CRYPTO);
}
```

This only checks consistency between the recovered scalar and the `Q` embedded in the ciphertext. Since `Q` is attacker-controlled (deserialized directly from the blob with no external binding), this check is trivially satisfied by any attacker who chooses `x` and sets `Q = x*G`.

**Attack construction:**

The attacker chooses a target scalar `x`, sets `Q = x*G`, sets `b = 0` (all bits zero, so `bi = false` for every row), then for row `i=0`:

1. Picks any `r[0]`
2. Computes `x_bi = DRBG(r[0]).gen_bn(q)` (deterministic, same computation `restore_from_decrypted` will perform)
3. Computes `x_bi_bar = x - x_bi mod q`
4. Computes `inner_label = genPVELabelWithPoint(caller_label, Q)` — both inputs are known to the attacker
5. Encrypts `x_bi_bar` under the legitimate public `ek` with `inner_label` to produce `c[0]`
6. Sets all other `c[i]` to garbage (they fail decryption and are skipped via `continue`)

When the honest decryptor calls `decrypt()`:
- `skip_verify=true` → `verify()` is bypassed entirely
- Row 0 decrypts successfully to `x_bi_bar`
- `restore_from_decrypted` computes `x_value = x_bi_bar + x_bi = x mod q`
- `x_value * G = Q` ✓ — passes
- Returns `SUCCESS` with `x_out = x`

Calling `verify()` on the same blob returns `E_CRYPTO` because `b_tag != b`.

### Impact Explanation

The PVE scheme's security guarantee is that the ciphertext is *publicly verifiable*: anyone holding `ek` can confirm the ciphertext is a valid encryption of the private key for `Q`. Skipping `verify()` on the decrypt path destroys this guarantee entirely. An attacker who controls the ciphertext blob can substitute any `(x, Q)` pair. The decryptor returns an attacker-chosen private key scalar, and the caller has no indication the proof was never checked. Depending on how the recovered scalar is used (key import, signing key restoration, share recovery), this enables key substitution with full attacker control over the recovered material.

### Likelihood Explanation

The `skip_verify=true` flag is hard-coded at every API decrypt call site — it is not a caller option, not gated on a trust level, and not documented as requiring a prior `verify()` call. Any caller who passes an attacker-supplied ciphertext blob to `decrypt()`, `decrypt_batch()`, or `combine_ac()` is affected. The attack requires only the ability to supply the ciphertext bytes and knowledge of the `ek` (public) and the label (often fixed or predictable).

### Recommendation

Remove `skip_verify=true` from all three API-layer decrypt call sites. The `verify()` step is the cryptographic core of PVE; it must run before decryption, not be optionally skipped. If performance is a concern for the batch/AC paths, the proof can be verified once before iterating rows, but it must not be omitted. If there is a legitimate use case for `skip_verify` (e.g., internal protocol steps where the caller has already verified), that path should be internal-only and not reachable from the public API.

### Proof of Concept

```
1. Generate a legitimate (ek, dk) key pair.
2. Choose any scalar x; compute Q = x*G.
3. Set b = 0 (128 zero bits).
4. For row i=0:
   a. Choose r[0] = any 16-byte value.
   b. Compute x_bi = DRBG_AES_CTR(r[0]).gen_bn(q).
   c. Compute x_bi_bar = (x - x_bi) mod q.
   d. inner_label = label || "-" || hex(SHA256(Q)).
   e. c[0] = base_pke.encrypt(ek, inner_label, x_bi_bar.to_bin(), rho=any).
5. Set x_rows[0..kappa-1] = 0, r[1..kappa-1] = random, c[1..kappa-1] = garbage.
6. Serialize into pve_ciphertext_blob_v1_t.
7. Call coinbase::api::pve::decrypt(curve, dk, ek, blob, label, out_x).
   → Returns SUCCESS, out_x == x.
8. Call coinbase::api::pve::verify(curve, ek, blob, Q_compressed, label).
   → Returns E_CRYPTO (b_tag != b).
```

Steps 7 and 8 confirm the API/internal disagreement: `decrypt` accepts the forged blob and returns the attacker-chosen scalar; `verify` correctly rejects it.

---

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** src/cbmpc/api/pve_base_pke.cpp (L277-279)
```cpp
  coinbase::crypto::bn_t x_bn;
  rv = pve_ct.decrypt(bridge, coinbase::mpc::pve_keyref(dk_mem), coinbase::mpc::pve_keyref(ek_mem), label, icurve, x_bn,
                      /*skip_verify=*/true);
```

**File:** src/cbmpc/protocol/pve.cpp (L70-115)
```cpp
error_t ec_pve_t::verify(const pve_base_pke_i& base_pke, pve_keyref_t ek, const ecc_point_t& Q, mem_t label) const {
  error_t rv = UNINITIALIZED_ERROR;
  ecurve_t curve = Q.get_curve();
  if (rv = curve.check(Q)) return coinbase::error(rv, "ec_pve_t::verify: check Q failed");
  if (Q != this->Q) return coinbase::error(E_CRYPTO, "public key (Q) mismatch");
  if (label != L) return coinbase::error(E_CRYPTO, "label mismatch");
  buf_t inner_label = genPVELabelWithPoint(label, Q);

  const auto& G = curve.generator();
  const mod_t& q = curve.order();
  const int max_scalar_size = q.get_bin_size();

  buf_t c0[kappa];
  buf_t c1[kappa];
  ecc_point_t X0[kappa];
  ecc_point_t X1[kappa];

  for (int i = 0; i < kappa; i++) {
    if (x_rows[i].get_bin_size() > max_scalar_size) return coinbase::error(E_CRYPTO);
    if (!q.is_in_range(x_rows[i])) return coinbase::error(E_CRYPTO);

    bool bi = b.get_bit(i);

    crypto::drbg_aes_ctr_t drbg(r[i]);

    bn_t xi;
    if (bi)
      xi = x_rows[i];
    else
      xi = drbg.gen_bn(q);
    buf_t rho = drbg.gen(rho_size);

    X0[i] = xi * G;
    X1[i] = Q - X0[i];
    if (rv = base_pke.encrypt(ek, inner_label, xi.to_bin(), rho, c0[i])) return rv;
    c1[i] = c[i];

    if (bi) {
      std::swap(X0[i], X1[i]);
      std::swap(c0[i], c1[i]);
    }
  }

  buf_t b_tag = crypto::ro::hash_string(Q, label, c0, c1, X0, X1).bitlen(kappa);
  if (b_tag != b) return coinbase::error(E_CRYPTO, "b' != b");
  return SUCCESS;
```

**File:** src/cbmpc/protocol/pve.cpp (L138-144)
```cpp
  MODULO(q) x_value = x_bi_bar + x_bi;

  if (x_value * G != Q) {
    x_value = 0;
    return coinbase::error(E_CRYPTO);
  }
  return SUCCESS;
```

**File:** src/cbmpc/protocol/pve.cpp (L147-151)
```cpp
error_t ec_pve_t::decrypt(const pve_base_pke_i& base_pke, pve_keyref_t dk, pve_keyref_t ek, mem_t label, ecurve_t curve,
                          bn_t& x_out, bool skip_verify) const {
  error_t rv = UNINITIALIZED_ERROR;
  if (!skip_verify && (rv = verify(base_pke, ek, Q, label))) return rv;

```

**File:** src/cbmpc/api/pve_batch_single_recipient.cpp (L172-175)
```cpp
  std::vector<coinbase::crypto::bn_t> xs_bn;
  rv = pve_ct.decrypt(bridge, coinbase::mpc::pve_keyref(dk_mem), coinbase::mpc::pve_keyref(ek_mem), label, icurve,
                      xs_bn, /*skip_verify=*/true);
  if (rv) {
```

**File:** src/cbmpc/api/pve_batch_ac.cpp (L353-356)
```cpp
  std::vector<coinbase::crypto::bn_t> xs_bn;
  rv = pve_ct.aggregate_to_restore_row(bridge, ac_internal, attempt_index, label, quorum_bn, xs_bn,
                                       /*skip_verify=*/true, pk_ptrs);
  if (rv) {
```
