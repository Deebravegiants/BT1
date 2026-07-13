The code is clear. Let me trace the exact execution path for the claimed scenario.

The code is fully traced. Here is the assessment:

---

### Title
Cross-Key Scalar Injection in 2PC `attach_private_scalar` Produces Blob with Mismatched Q and x_share — (`src/cbmpc/api/schnorr2pc.cpp`)

### Summary

The 2PC `attach_private_scalar` function accepts a private scalar from key K2 paired with a public blob from key K1 and returns `SUCCESS`, producing a key blob whose global public key `Q` belongs to K1 but whose `x_share` belongs to K2. The only guard performed is `x*G == Qi_self` (line 221), where `Qi_self` is the caller-supplied `public_share_compressed` — not any value anchored in the blob. Because the 2PC blob format does not store Qi, there is no blob-side value to compare against, and the check is trivially satisfied by any consistent (x, x*G) pair regardless of which key it came from.

### Finding Description

**2PC blob structure** — `key_blob_v1_t` in `src/cbmpc/api/schnorr2pc.cpp` stores only `{version, role, curve, Q_compressed, x_share}`. There is no `Qi` (per-party share public point) field. [1](#0-0) 

**MP blob structure** — `key_blob_v1_t` in `src/cbmpc/api/schnorr_mp.cpp` stores `Qis_compressed` (a map of party name → compressed Qi), which is the anchor used to bind the caller-supplied `public_share_compressed` to the blob. [2](#0-1) 

**MP guard (present)** — The MP `attach_private_scalar` first looks up `Qi_self_compressed` from the blob's `Qis_compressed` map and explicitly rejects any `public_share_compressed` that does not match it: [3](#0-2) 

**2PC guard (absent)** — The 2PC `attach_private_scalar` has no equivalent lookup. It only checks `x * G != Qi_self` where `Qi_self` is decoded directly from the caller-supplied `public_share_compressed`. There is no comparison against any blob-resident value: [4](#0-3) 

**Execution path for the cross-key injection:**

Given:
- `public_blob_K1` = output of `detach_private_scalar(K1)` → contains `Q_K1`, `x_share = q` (out-of-range sentinel)
- `x_K2` = P1's scalar from K2
- `Qi_K2 = x_K2 * G`

Call: `attach_private_scalar(public_blob_K1, x_K2, Qi_K2)`

1. Blob parsed → `pub.Q_compressed = Q_K1`, `pub.x_share = q` (sentinel, not used further)
2. `Qi_self` decoded from caller-supplied `Qi_K2` → valid curve point ✓
3. `x = x_K2 % q` → in range ✓
4. `x_K2 * G == Qi_K2` → **trivially true** ✓
5. `Q_K1` decoded and validated ✓
6. `pub.x_share = x_K2` written; blob serialized with `{Q_K1, x_K2}`
7. Returns `SUCCESS`

The resulting blob has `Q = Q_K1` and `x_share = x_K2` — a semantically invalid combination. [5](#0-4) 

**Downstream deserialization** — `deserialize_key_blob` / `blob_to_key` only checks that `x_share` is in range and that `Q_compressed` decodes to a valid point. It does not verify `x_share * G == Q` or any Qi relationship, so the corrupted blob passes deserialization silently: [6](#0-5) 

### Impact Explanation

The corrupted blob is accepted by `sign` and `refresh`. During a 2PC signing session, P1 uses `x_K2` as its share while P2 uses its correct share for K1. The combined signing computation produces a signature that is invalid under `Q_K1`. The signing API returns `SUCCESS` (no protocol-level consistency check catches the mismatch), but the output signature fails BIP340 verification under the key the caller believes they are signing with. This is unsafe state acceptance: the library accepts an invalid input combination and emits a cryptographically invalid output without signaling an error.

### Likelihood Explanation

Exploiting this requires a caller who legitimately holds two distinct 2PC key blobs (K1 and K2) for the same party role and who calls `detach_private_scalar` on both. This is a realistic scenario in backup/restore workflows (e.g., PVE batch backup as shown in `demo-api/schnorr_2p_pve_batch_backup/main.cpp`). The API surface is public and the call sequence requires no special privilege beyond holding two key blobs.


### Recommendation

Store `Qi_compressed` in the 2PC `key_blob_v1_t` (analogous to `Qis_compressed` in the MP blob). In `detach_private_scalar`, compute and persist `Qi = x_share * G` before zeroing the scalar. In `attach_private_scalar`, look up the stored `Qi_compressed` and reject any `public_share_compressed` that does not match it byte-for-byte, mirroring the MP guard at lines 522–527 of `src/cbmpc/api/schnorr_mp.cpp`.

### Proof of Concept

```
1. DKG → K1: P1 gets key_blob_K1 (Q_K1, x_K1), P2 gets key_blob_K1_p2
2. DKG → K2: P1 gets key_blob_K2 (Q_K2, x_K2), P2 gets key_blob_K2_p2
3. detach_private_scalar(key_blob_K1) → (public_blob_K1, x_K1_fixed)
4. get_public_share_compressed(key_blob_K2) → Qi_K2  [= x_K2 * G]
5. detach_private_scalar(key_blob_K2) → (_, x_K2_fixed)
6. attach_private_scalar(public_blob_K1, x_K2_fixed, Qi_K2) → corrupted_blob  [returns SUCCESS]
7. sign(job_p1, corrupted_blob, msg) + sign(job_p2, key_blob_K1_p2, msg) → sig  [returns SUCCESS]
8. bip340::verify(Q_K1, msg, sig) → FAIL  [invalid signature]
```

### Citations

**File:** src/cbmpc/api/schnorr2pc.cpp (L18-27)
```cpp
struct key_blob_v1_t {
  uint32_t version = key_blob_version_v1;
  uint32_t role = 0;   // 0=p1, 1=p2
  uint32_t curve = 0;  // coinbase::api::curve_id

  buf_t Q_compressed;
  coinbase::crypto::bn_t x_share;

  void convert(coinbase::converter_t& c) { c.convert(version, role, curve, Q_compressed, x_share); }
};
```

**File:** src/cbmpc/api/schnorr2pc.cpp (L29-41)
```cpp
static error_t blob_to_key(const key_blob_v1_t& blob, coinbase::mpc::schnorr2p::key_t& key) {
  if (blob.role > 1) return coinbase::error(E_FORMAT, "invalid key blob role");
  if (static_cast<curve_id>(blob.curve) != curve_id::secp256k1)
    return coinbase::error(E_FORMAT, "invalid key blob curve");

  key.role = static_cast<coinbase::mpc::party_t>(static_cast<int32_t>(blob.role));
  key.curve = coinbase::crypto::curve_secp256k1;
  const auto& q = key.curve.order();
  if (!q.is_in_range(blob.x_share)) return coinbase::error(E_FORMAT, "invalid key blob");
  key.x_share = blob.x_share;

  return key.Q.from_bin(key.curve, blob.Q_compressed);
}
```

**File:** src/cbmpc/api/schnorr2pc.cpp (L212-221)
```cpp
  coinbase::crypto::ecc_point_t Qi_self(curve);
  if (rv = Qi_self.from_bin(curve, public_share_compressed))
    return coinbase::error(rv, "invalid public_share_compressed");
  if (rv = curve.check(Qi_self)) return coinbase::error(rv, "invalid public_share_compressed");

  const coinbase::crypto::bn_t x = coinbase::crypto::bn_t::from_bin(private_scalar_fixed) % q;
  if (!q.is_in_range(x)) return coinbase::error(E_FORMAT, "invalid private_scalar_fixed");

  const auto& G = curve.generator();
  if (x * G != Qi_self) return coinbase::error(E_FORMAT, "x_share mismatch key blob");
```

**File:** src/cbmpc/api/schnorr2pc.cpp (L228-231)
```cpp
  pub.x_share = x;
  pub.Q_compressed = Q.to_compressed_bin();
  out_key_blob = coinbase::convert(pub);
  return SUCCESS;
```

**File:** src/cbmpc/api/schnorr_mp.cpp (L24-38)
```cpp
struct key_blob_v1_t {
  uint32_t version = key_blob_version_v1;
  uint32_t curve = 0;  // coinbase::api::curve_id

  std::string party_name;  // self identity (name-bound, not index-bound)

  buf_t Q_compressed;
  std::map<std::string, buf_t> Qis_compressed;  // name -> compressed Qi

  coinbase::crypto::bn_t x_share;

  void convert(coinbase::converter_t& c) {
    c.convert(version, curve, party_name, Q_compressed, Qis_compressed, x_share);
  }
};
```

**File:** src/cbmpc/api/schnorr_mp.cpp (L522-527)
```cpp
  const auto it = blob.Qis_compressed.find(blob.party_name);
  if (it == blob.Qis_compressed.end()) return coinbase::error(E_FORMAT, "key blob missing self Qi");
  const buf_t& Qi_self_compressed = it->second;

  if (public_share_compressed != mem_t(Qi_self_compressed))
    return coinbase::error(E_BADARG, "public_share_compressed mismatch key blob");
```
