I need to trace the full call path carefully to determine if the batch-count mismatch can actually produce a `SUCCESS` return with wrong-count output.

### Title
Batch-Count Field in `pve_ac_ciphertext_blob_v1_t` Is Parsed But Never Enforced in `combine_ac`, Allowing Attacker-Controlled Mismatch Between API-Layer Count and Protocol-Layer Output — (`src/cbmpc/api/pve_batch_ac.cpp`)

---

### Summary

`combine_ac` parses `blob.batch_count` (N) from the outer envelope but then completely ignores it. The actual batch size used for decryption is `pve_ct.get_Q().size()` (M) from the inner `ec_pve_ac_t`. An attacker who controls the ciphertext blob can set `blob.batch_count = N` while embedding an inner object with `M != N` Q-points. `combine_ac` returns `SUCCESS` with `out_xs.size() == M`, while `get_ac_batch_count` returns N — a silent API-layer / protocol-layer disagreement.

---

### Finding Description

**`parse_ac_ciphertext`** validates only three things about the outer envelope: [1](#0-0) 

It checks `version`, `batch_count != 0`, and `batch_count <= MAX_BATCH_COUNT`. It does **not** check that the inner object's Q-vector length equals `batch_count`.

**`combine_ac`** then:
1. Parses the blob (line 331), obtaining `blob.batch_count = N`.
2. Deserializes the inner `ec_pve_ac_t` from `blob.ct` (line 334), which carries M Q-points.
3. Checks only the **curve** of each Q-point (lines 336–338), never the **count**.
4. Calls `aggregate_to_restore_row` with `skip_verify=true` (line 354–355).
5. Builds `out_xs` directly from `xs_bn.size()` (lines 361–365) — which is M, not N. [2](#0-1) 

After line 331, `blob.batch_count` (N) is **never referenced again** in `combine_ac`.

Inside `aggregate_to_restore_row`, `batch_size` is derived exclusively from `Q.size()`: [3](#0-2) 

The AES-GCM key derivation uses `L = hash(label, Q)` where Q has M points: [4](#0-3) 

Because the attacker constructed the inner `ec_pve_ac_t` with M Q-points and encrypted all rows using `L = hash(label, Q_M)`, the AES-GCM decryption succeeds (the AAD matches). The size check at line 278 uses `batch_size = M`, which is internally consistent: [5](#0-4) 

The function returns `SUCCESS` with `x.size() == M`. Back in `combine_ac`, `out_xs` is populated with M elements and `SUCCESS` is returned — while `get_ac_batch_count` on the same ciphertext returns N. [6](#0-5) 

The missing guard — absent from both `parse_ac_ciphertext` and `combine_ac` — is:
```cpp
if (pve_ct.get_Q().size() != static_cast<size_t>(blob.batch_count))
    return coinbase::error(E_BADARG, "batch count mismatch");
```

---

### Impact Explanation

An attacker who supplies a crafted ciphertext blob (e.g., as a malicious transport peer or Byzantine participant providing a recovery ciphertext) can make `combine_ac` return `SUCCESS` with `out_xs.size() == M` while the caller believes the batch size is N (from `get_ac_batch_count` or from the original encryption context). If the caller uses `out_xs` without independently re-checking its length against the expected count:

- **M < N**: recovered key material is silently truncated — the caller processes fewer scalars than expected, potentially missing key shares.
- **M > N**: the caller processes extra scalars that were not part of the original batch, potentially substituting attacker-chosen key material for indices beyond the legitimate batch.

This falls under the **High** impact scope: attacker-controlled ciphertext is accepted with a wrong batch count, causing the API layer and protocol layer to disagree about the number of recovered scalars.

---

### Likelihood Explanation

The attack requires only the ability to supply a crafted ciphertext blob to `combine_ac` (or `cbmpc_pve_ac_combine`). No threshold collusion, no private key material, and no cryptographic forgery is needed. The attacker simply:
1. Legitimately encrypts M scalars to obtain a valid `ec_pve_ac_t` with M Q-points.
2. Re-serializes the outer blob with `batch_count` patched to N.

The partial-decrypt step (`partial_decrypt_ac_attempt`) is also affected: it does not check `Q.size() == blob.batch_count` either, so shares produced from a mismatched ciphertext are consistent with M, not N. [7](#0-6) 

---

### Recommendation

Add a consistency check in `combine_ac` immediately after deserializing the inner object:

```cpp
if (pve_ct.get_Q().size() != static_cast<size_t>(blob.batch_count))
    return coinbase::error(E_BADARG, "batch count mismatch between envelope and ciphertext");
```

The same check should be added in `partial_decrypt_ac_attempt` and `verify_ac` for defense-in-depth. Optionally, move the check into `parse_ac_ciphertext` after deserializing the inner object, so all callers benefit automatically.

---

### Proof of Concept

```
1. Encrypt M=3 scalars with a valid quorum → obtain ciphertext blob_M.
2. Deserialize blob_M to get (version=1, batch_count=3, ct=<ec_pve_ac_t with 3 Q-points>).
3. Re-serialize with batch_count patched to N=5 → crafted_blob.
4. Call get_ac_batch_count(crafted_blob) → returns 5.
5. Call partial_decrypt_ac_attempt for each quorum member using crafted_blob → succeeds (inner object is valid for M=3).
6. Call combine_ac(crafted_blob, quorum_shares) → returns SUCCESS with out_xs.size() == 3.
7. Assert: get_ac_batch_count returned 5, but out_xs.size() == 3 — mismatch accepted as SUCCESS.
```

### Citations

**File:** src/cbmpc/api/pve_batch_ac.cpp (L29-37)
```cpp
static error_t parse_ac_ciphertext(mem_t ciphertext, pve_ac_ciphertext_blob_v1_t& out_blob) {
  error_t rv = coinbase::convert(out_blob, ciphertext);
  if (rv) return rv;
  if (out_blob.version != pve_ac_ciphertext_version_v1)
    return coinbase::error(E_FORMAT, "unsupported ciphertext version");
  if (out_blob.batch_count == 0) return coinbase::error(E_FORMAT, "invalid batch count");
  if (out_blob.batch_count > static_cast<uint32_t>(MAX_BATCH_COUNT)) return coinbase::error(E_RANGE, "batch too large");
  return SUCCESS;
}
```

**File:** src/cbmpc/api/pve_batch_ac.cpp (L231-253)
```cpp
  pve_ac_ciphertext_blob_v1_t blob;
  if (rv = parse_ac_ciphertext(ciphertext, blob)) return rv;

  coinbase::mpc::ec_pve_ac_t pve_ct;
  if (rv = coinbase::convert(pve_ct, blob.ct)) return rv;

  for (const auto& q : pve_ct.get_Q()) {
    if (q.get_curve() != icurve) return coinbase::error(E_BADARG, "ciphertext curve mismatch");
  }

  detail::base_pke_bridge_t bridge(base_pke);

  const coinbase::mem_t dk_mem(dk.data, dk.size);
  coinbase::crypto::bn_t share_bn;
  rv = pve_ct.party_decrypt_row(bridge, ac_internal, attempt_index, std::string(leaf_name),
                                coinbase::mpc::pve_keyref(dk_mem), label, share_bn);
  if (rv) {
    out_share.free();
    return rv;
  }

  out_share = share_bn.to_bin(icurve.order().get_bin_size());
  return SUCCESS;
```

**File:** src/cbmpc/api/pve_batch_ac.cpp (L330-366)
```cpp
  pve_ac_ciphertext_blob_v1_t blob;
  if (rv = parse_ac_ciphertext(ciphertext, blob)) return rv;

  coinbase::mpc::ec_pve_ac_t pve_ct;
  if (rv = coinbase::convert(pve_ct, blob.ct)) return rv;

  for (const auto& q : pve_ct.get_Q()) {
    if (q.get_curve() != icurve) return coinbase::error(E_BADARG, "ciphertext curve mismatch");
  }

  const int expected_share_size = icurve.order().get_bin_size();
  for (const auto& [name_view, share_bytes] : quorum_shares) {
    if (share_bytes.size != expected_share_size) return coinbase::error(E_BADARG, "quorum_shares: invalid share size");
  }

  std::map<std::string, coinbase::crypto::bn_t> quorum_bn;
  for (const auto& [name_view, share_bytes] : quorum_shares) {
    quorum_bn.emplace(std::string(name_view), coinbase::crypto::bn_t::from_bin(share_bytes));
  }

  detail::base_pke_bridge_t bridge(base_pke);
  coinbase::mpc::ec_pve_ac_t::pks_t pk_ptrs;

  std::vector<coinbase::crypto::bn_t> xs_bn;
  rv = pve_ct.aggregate_to_restore_row(bridge, ac_internal, attempt_index, label, quorum_bn, xs_bn,
                                       /*skip_verify=*/true, pk_ptrs);
  if (rv) {
    out_xs.clear();
    return rv;
  }

  std::vector<buf_t> out_local;
  out_local.resize(xs_bn.size());
  const int out_len = icurve.order().get_bin_size();
  for (size_t i = 0; i < xs_bn.size(); i++) out_local[i] = xs_bn[i].to_bin(out_len);
  out_xs = std::move(out_local);
  return SUCCESS;
```

**File:** src/cbmpc/protocol/pve_ac.cpp (L247-247)
```cpp
  int batch_size = int(Q.size());
```

**File:** src/cbmpc/protocol/pve_ac.cpp (L253-263)
```cpp
  buf_t L = crypto::sha256_t::hash(label, Q);

  bn_t K;
  if (rv = ac.reconstruct(q, quorum_decrypted, K)) return rv;

  buf_t k_and_iv = crypto::ro::hash_string(K, L).bitlen(256 + iv_bitlen);
  mem_t k_aes = k_and_iv.take(32);
  mem_t iv = k_and_iv.skip(32);

  buf_t decrypted_data;
  if (rv = crypto::aes_gcm_t::decrypt(k_aes, iv, L, tag_size, row.c, decrypted_data)) return rv;
```

**File:** src/cbmpc/protocol/pve_ac.cpp (L278-286)
```cpp
  if (x_bin.size != batch_size * curve_size) return coinbase::error(E_CRYPTO);
  crypto::drbg_aes_ctr_t drbg(seed);
  x.resize(batch_size);
  for (int j = 0; j < batch_size; j++) {
    bn_t x0 = drbg.gen_bn(q);
    bn_t x1 = bn_t::from_bin(x_bin.range(j * curve_size, curve_size));
    MODULO(q) x[j] = x0 + x1;
    if (x[j] * G != Q[j]) return coinbase::error(E_CRYPTO);
  }
```
