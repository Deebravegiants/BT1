### Title
TDH2 Partial Decryption Proof Omits Label — Label-Substitution Lets Attacker Reuse Partial Decryptions Across Contexts - (File: `src/cbmpc/crypto/tdh2.cpp`)

### Summary
In `private_share_t::decrypt`, the `label` parameter is accepted and used to verify the ciphertext, but is **never forwarded** into the ZK proof hash. The matching verifier `check_partial_decryption_helper` also omits the label. A malicious encryptor who controls the ephemeral scalar `r` can craft two ciphertexts sharing the same `R1` under different labels, collect honest-party partial decryptions for one label, and replay them through the public `combine_additive` / `combine_ac` API to obtain a successful decryption under the second label — without the honest parties ever agreeing to decrypt that context.

### Finding Description

In `private_share_t::decrypt` the proof challenge is computed as:

```cpp
// src/cbmpc/crypto/tdh2.cpp  lines 85-90
bn_t si = curve.get_random_value();
ecc_point_t Yi = si * R1;
ecc_point_t Zi = si * G;

ei = ro::hash_number(Xi, Yi, Zi).mod(q);   // ← label absent
MODULO(q) fi = si + x * ei;
``` [1](#0-0) 

The `label` argument is consumed only by the earlier `ciphertext.verify(pub_key, label)` call:

```cpp
// src/cbmpc/crypto/tdh2.cpp  line 72
if (rv = ciphertext.verify(pub_key, label)) return rv;
``` [2](#0-1) 

The verifier mirrors the same omission:

```cpp
// src/cbmpc/crypto/tdh2.cpp  lines 118-122
ecc_point_t Yi = fi * R1 - ei * Xi;
ecc_point_t Zi = fi * G  - ei * Qi;

bn_t ei_test = ro::hash_number(Xi, Yi, Zi).mod(q);  // ← label absent
if (ei != ei_test) return coinbase::error(E_CRYPTO);
``` [3](#0-2) 

Because the proof binds only to `R1` (not to the label), any two ciphertexts that share the same ephemeral point `R1 = r·G` will accept the same set of partial decryptions, regardless of their labels.

**Attack path through the public API:**

1. Attacker (as encryptor, knowing `r`) calls the internal `public_key_t::encrypt(plain1, L1, r, s1, iv1)` to produce `C1` and `public_key_t::encrypt(plain2, L2, r, s2, iv2)` to produce `C2`. Both share `R1 = r·G`. [4](#0-3) 

2. Honest parties call the public API `coinbase::api::tdh2::partial_decrypt(private_share, C1, L1, pd_i)`. Each call verifies `C1` against `L1` and produces `(Xi, ei, fi)` bound only to `R1`. [5](#0-4) 

3. Attacker calls the public API `coinbase::api::tdh2::combine_additive(pk, Qi, L2, {pd_i}, C2, plaintext)`. [6](#0-5) 

4. Inside `combine_additive`, `ciphertext.verify(pk, L2)` passes (C2 is a legitimately formed ciphertext for L2). Then `check_partial_decryption_helper(Qi[rid-1], C2, curve)` passes because `C2.R1 == C1.R1` and the proof contains no label commitment. Decryption of `C2` succeeds. [7](#0-6) 

The first bad trust transition is inside `check_partial_decryption_helper`: it accepts a partial decryption produced under label `L1` as valid evidence for label `L2`, because the label was never forwarded into the proof. [8](#0-7) 

### Impact Explanation
The label is the sole mechanism for binding a partial decryption to a specific decryption context. Omitting it from the proof hash means honest parties' partial decryptions are portable across any ciphertext that reuses the same ephemeral `R1`. In deployments where labels encode authorization context (e.g., "recover key for account A" vs. "recover key for account B"), a malicious encryptor can obtain a threshold-authorized decryption for a context the honest parties never consented to, satisfying the "attacker-controlled labels accepted under the wrong label" criterion in the High impact scope.

### Likelihood Explanation
The encryptor role is a realistic adversarial position: in key-backup or escrow workflows the entity requesting encryption is distinct from the threshold keyholders. The internal `encrypt(plain, label, r, s, iv)` overload is part of the shipped library and is directly callable. The public `combine_additive` and `combine_ac` APIs accept arbitrary serialized partial decryptions with no additional label binding check.

### Recommendation
Include the label in the proof challenge hash in both the prover and verifier:

```cpp
// prover (private_share_t::decrypt)
ei = ro::hash_number(Xi, Yi, Zi, label).mod(q);

// verifier (check_partial_decryption_helper) — requires label to be threaded in
bn_t ei_test = ro::hash_number(Xi, Yi, Zi, label).mod(q);
```

`check_partial_decryption_helper` must be updated to accept `mem_t label` and all call sites (`combine_additive`, `combine`) must pass the label through.

### Proof of Concept

```cpp
// Attacker controls r; creates C1 (label L1) and C2 (label L2) with same R1.
bn_t r = curve.get_random_value();
bn_t s1 = curve.get_random_value(), s2 = curve.get_random_value();
buf_t iv1 = gen_random(16), iv2 = gen_random(16);

auto C1 = pk.encrypt(plain1, mem_t("L1"), r, s1, iv1);
auto C2 = pk.encrypt(plain2, mem_t("L2"), r, s2, iv2);
// C1.R1 == C2.R1 == r*G

// Honest parties partially decrypt C1 under L1 via public API.
partial_decryption_t pd;
share.decrypt(C1, mem_t("L1"), pd);   // succeeds; ei = hash(Xi,Yi,Zi) — no label

// Attacker replays pd against C2 under L2 via public API.
buf_t plaintext;
// combine_additive calls check_partial_decryption_helper(Qi, C2, curve)
// which recomputes hash(Xi, Yi', Zi') using C2.R1 == C1.R1 → passes
coinbase::crypto::tdh2::combine_additive(pk, {Qi}, mem_t("L2"), {pd}, C2, plaintext);
// plaintext == plain2, obtained without honest parties ever consenting to decrypt L2
```

### Citations

**File:** src/cbmpc/crypto/tdh2.cpp (L68-72)
```cpp
error_t private_share_t::decrypt(const ciphertext_t& ciphertext, mem_t label,
                                 partial_decryption_t& partial_decryption) const {
  error_t rv = UNINITIALIZED_ERROR;
  const auto& curve = pub_key.Q.get_curve();
  if (rv = ciphertext.verify(pub_key, label)) return rv;
```

**File:** src/cbmpc/crypto/tdh2.cpp (L85-90)
```cpp
  bn_t si = curve.get_random_value();
  ecc_point_t Yi = si * R1;
  ecc_point_t Zi = si * G;

  ei = ro::hash_number(Xi, Yi, Zi).mod(q);
  MODULO(q) fi = si + x * ei;
```

**File:** src/cbmpc/crypto/tdh2.cpp (L104-125)
```cpp
error_t partial_decryption_t::check_partial_decryption_helper(const ecc_point_t& Qi, const ciphertext_t& ciphertext,
                                                              ecurve_t curve) const {
  error_t rv = UNINITIALIZED_ERROR;

  if (rv = curve.check(Qi))
    return coinbase::error(rv, "partial_decryption_t::check_partial_decryption_helper: check Qi failed");
  if (rv = curve.check(Xi))
    return coinbase::error(rv, "partial_decryption_t::check_partial_decryption_helper: check Xi failed");

  const auto& G = curve.generator();
  const mod_t& q = curve.order();
  if (!q.is_in_range(ei) || !q.is_in_range(fi)) return coinbase::error(E_CRYPTO);

  const ecc_point_t& R1 = ciphertext.R1;
  ecc_point_t Yi = fi * R1 - ei * Xi;
  ecc_point_t Zi = fi * G - ei * Qi;

  bn_t ei_test = ro::hash_number(Xi, Yi, Zi).mod(q);
  if (ei != ei_test) return coinbase::error(E_CRYPTO);

  return SUCCESS;
}
```

**File:** src/cbmpc/crypto/tdh2.cpp (L127-152)
```cpp
error_t combine_additive(const public_key_t& pub_key, const pub_shares_t& Qi, mem_t label,
                         const partial_decryptions_t& partial_decryptions, const ciphertext_t& ciphertext,
                         buf_t& plain) {
  error_t rv = UNINITIALIZED_ERROR;
  const auto& curve = pub_key.Q.get_curve();
  int n = int(Qi.size());
  for (const auto& _Qi : Qi) {
    if (rv = curve.check(_Qi)) return coinbase::error(rv, "combine_additive: check Qi failed");
  }
  if ((int)partial_decryptions.size() != n) return coinbase::error(E_CRYPTO);

  if (rv = ciphertext.verify(pub_key, label)) return rv;

  ecc_point_t V = curve.infinity();
  for (int i = 0; i < n; i++) {
    const partial_decryption_t& partial_decryption = partial_decryptions[i];

    const int rid = partial_decryption.rid;
    if (rid < 1 || rid > n) return coinbase::error(E_CRYPTO);
    if (rv = partial_decryption.check_partial_decryption_helper(Qi[rid - 1], ciphertext, curve)) return rv;

    V += partial_decryption.Xi;
  }

  if (rv = ciphertext.decrypt(V, plain, label)) return rv;
  return SUCCESS;
```

**File:** include-internal/cbmpc/internal/crypto/tdh2.h (L60-60)
```text
  ciphertext_t encrypt(mem_t plain, mem_t label, const bn_t& r, const bn_t& s, mem_t iv) const;
```

**File:** src/cbmpc/api/tdh2.cpp (L213-235)
```cpp
error_t partial_decrypt(mem_t private_share, mem_t ciphertext, mem_t label, buf_t& partial_decryption) {
  if (const error_t rv = coinbase::api::detail::validate_mem_arg_max_size(private_share, "private_share",
                                                                          coinbase::api::detail::MAX_OPAQUE_BLOB_SIZE))
    return rv;
  if (const error_t rv = coinbase::api::detail::validate_mem_arg_max_size(
          ciphertext, "ciphertext", coinbase::api::detail::MAX_CIPHERTEXT_BLOB_SIZE))
    return rv;
  if (const error_t rv = coinbase::api::detail::validate_mem_arg(label, "label")) return rv;

  coinbase::crypto::tdh2::private_share_t share;
  error_t rv = deserialize_private_share(private_share, share);
  if (rv) return rv;

  coinbase::crypto::tdh2::ciphertext_t ct;
  rv = coinbase::convert(ct, ciphertext);
  if (rv) return rv;

  coinbase::crypto::tdh2::partial_decryption_t partial;
  rv = share.decrypt(ct, label, partial);
  if (rv) return rv;

  partial_decryption = coinbase::convert(partial);
  return SUCCESS;
```

**File:** src/cbmpc/api/tdh2.cpp (L238-285)
```cpp
error_t combine_additive(mem_t public_key, const std::vector<mem_t>& public_shares, mem_t label,
                         const std::vector<mem_t>& partial_decryptions, mem_t ciphertext, buf_t& plaintext) {
  if (const error_t rv = coinbase::api::detail::validate_mem_arg_max_size(public_key, "public_key",
                                                                          coinbase::api::detail::MAX_OPAQUE_BLOB_SIZE))
    return rv;
  if (const error_t rv = coinbase::api::detail::validate_mem_arg(label, "label")) return rv;
  if (const error_t rv = coinbase::api::detail::validate_mem_arg_max_size(
          ciphertext, "ciphertext", coinbase::api::detail::MAX_CIPHERTEXT_BLOB_SIZE))
    return rv;
  if (const error_t rv = coinbase::api::detail::validate_mem_vec_arg_max_size(
          public_shares, "public_shares", coinbase::api::detail::MAX_OPAQUE_BLOB_SIZE))
    return rv;
  if (const error_t rv = coinbase::api::detail::validate_mem_vec_arg_max_size(
          partial_decryptions, "partial_decryptions", coinbase::api::detail::MAX_OPAQUE_BLOB_SIZE))
    return rv;

  if (public_shares.size() != partial_decryptions.size())
    return coinbase::error(E_BADARG, "public_shares and partial_decryptions size mismatch");

  coinbase::crypto::tdh2::public_key_t pk;
  error_t rv = pk.from_bin(public_key);
  if (rv) return rv;
  if (rv = validate_public_key(pk)) return rv;

  coinbase::crypto::tdh2::ciphertext_t ct;
  rv = coinbase::convert(ct, ciphertext);
  if (rv) return rv;

  auto curve = pk.Q.get_curve();
  if (!curve.valid()) return coinbase::error(E_FORMAT, "public key missing curve");

  coinbase::crypto::tdh2::pub_shares_t Qi;
  Qi.reserve(public_shares.size());
  for (const auto& m : public_shares) {
    coinbase::crypto::ecc_point_t P;
    rv = P.from_bin(curve, m);
    if (rv) return rv;
    Qi.emplace_back(std::move(P));
  }

  coinbase::crypto::tdh2::partial_decryptions_t partials;
  partials.resize(partial_decryptions.size());
  for (size_t i = 0; i < partial_decryptions.size(); i++) {
    rv = coinbase::convert(partials[i], partial_decryptions[i]);
    if (rv) return rv;
  }

  return coinbase::crypto::tdh2::combine_additive(pk, Qi, label, partials, ct, plaintext);
```
