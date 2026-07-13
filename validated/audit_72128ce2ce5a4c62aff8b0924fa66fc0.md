I have all the information needed. Let me trace the exact code path and validate the claim.

**Key code path:**

`blob_to_key` in `src/cbmpc/api/eddsa2pc.cpp` (lines 29–44):
- Checks `x_share ∈ [0, q)` ✓
- Calls `key.Q.from_bin(key.curve, blob.Q_compressed)` → `ec25519_core::from_bin` ✓
- Calls `key.curve.check(key.Q)` (valid subgroup point) ✓
- **No check that `x_share * G == Qi` or any binding between `x_share` and `Q`** ✗

Then in `schnorr_2p.cpp` `sign_batch` (lines 92–124):
- Challenge: `e = SHA512(R || key.Q || msg)` — uses `key.Q`
- P2 computes: `s2 = e * key.x_share + k2`
- P1 computes: `s = e * key.x_share + k1 + s2`
- P1 verifies: `pub_key.verify(msgs[i], sigs[i])` where `pub_key` wraps `key.Q`

If `Q` is inconsistent with `x_share`, the signature `s*G = R + e*(x1+x2)*G` won't equal `R + e*Q'` (the wrong Q), so P1's internal verify fails and P1 returns error. P2 has already returned SUCCESS after sending `s2` — it never receives anything back from P1.

**Contrast with multi-party version** — `eddsa_mp.cpp` line 158 explicitly has:
```cpp
if (blob.x_share * G != it_self->second) return coinbase::error(E_FORMAT, "invalid key blob");
```
And `attach_private_scalar` in `eddsa2pc.cpp` line 211 also has:
```cpp
if (x * G != Qi_self) return coinbase::error(E_FORMAT, "x_share mismatch key blob");
```
The 2PC `blob_to_key` is the only deserialization path that lacks this guard.

---

### Title
Missing `x_share * G == Qi` Binding Check in EdDSA-2P `blob_to_key` Enables Crafted Blob to Cause Honest-Party Divergence During Signing — (`src/cbmpc/api/eddsa2pc.cpp`)

### Summary
`blob_to_key` in the EdDSA-2P API layer validates that `x_share ∈ [0, q)` and that `Q` is a valid curve point, but does not verify any binding between them. An attacker who can supply a crafted `key_blob_v1_t` — with a valid `x_share` and an independently chosen valid `Q` — will pass all deserialization guards, enter the 2PC signing protocol, and cause P1 to abort at the internal `pub_key.verify` step while P2 returns SUCCESS, producing honest-party divergence.

### Finding Description

`blob_to_key` performs the following checks: [1](#0-0) 

It validates `x_share` is in range and `Q` is a valid point, but there is no check that `x_share * G == Qi` (the party's own share point). The blob format stores only the global public key `Q` and the scalar `x_share`, with no stored `Qi` to bind against. [2](#0-1) 

During signing, the EdDSA challenge is computed as `e = SHA512(R || key.Q || msg)`, and the final signature is verified against `key.Q`: [3](#0-2) 

If `Q` in the blob is not the actual global public key (i.e., `Q ≠ x1*G + x2*G`), the computed `s*G = R + e*(x1+x2)*G` will not equal `R + e*Q'`, so `pub_key.verify` returns an error on P1. P2 has already completed its last protocol step (sending `s2`) and returns SUCCESS. [4](#0-3) 

By contrast, the multi-party EdDSA deserialization explicitly enforces the binding: [5](#0-4) 

And `attach_private_scalar` in the same 2PC file also enforces it: [6](#0-5) 

The 2PC `blob_to_key` is the only deserialization path that omits this guard.

### Impact Explanation
A caller (or any entity that can supply a key blob to the `sign` API) can craft a `key_blob_v1_t` with an arbitrary valid `x_share` and an arbitrary valid but mismatched `Q`. The blob passes all validation in `deserialize_key_blob` → `blob_to_key` and returns `SUCCESS`. The full 2PC signing protocol then executes (consuming network round-trips), after which P1 aborts with a cryptographic error while P2 returns `SUCCESS`. This is honest-party divergence: one party believes signing succeeded, the other has aborted. Repeated injection causes persistent denial of signing for the affected key.

### Likelihood Explanation
The key blob is an opaque caller-managed byte string. Any entity that can write or substitute the blob file/record — including a compromised key-management service, a malicious application layer, or a storage-layer attacker — can trigger this without any cryptographic knowledge. The blob format is straightforward to reconstruct from the public header and source. The attack requires no interaction with the peer and no knowledge of the real key material; any valid scalar and any valid curve point suffice.

### Recommendation
Add a binding check in `blob_to_key` in `src/cbmpc/api/eddsa2pc.cpp`. Since the 2PC blob does not store `Qi` directly, compute it on the fly and store it, or add `Qi_compressed` to `key_blob_v1_t` (with a version bump) and verify `x_share * G == Qi` at deserialization time, mirroring the check already present in `attach_private_scalar` and in the multi-party deserialization path.

### Proof of Concept
1. Run DKG to obtain a legitimate `key_blob_1` for P1.
2. Deserialize `key_blob_1` to extract `x_share` and `Q`.
3. Construct a new `key_blob_v1_t` with the same `x_share` but replace `Q_compressed` with the encoding of a different valid Ed25519 point `Q'` (e.g., `2*G`).
4. Serialize the crafted blob.
5. Call `coinbase::api::eddsa_2p::sign(job1, crafted_blob, msg, sig1)` on P1 and `coinbase::api::eddsa_2p::sign(job2, key_blob_2, msg, sig2)` on P2 concurrently.
6. Assert: `deserialize_key_blob(crafted_blob, key)` returns `SUCCESS` (the blob passes all guards).
7. Assert: P1's `sign` returns a non-zero error code (from `pub_key.verify` failing at line 124 of `schnorr_2p.cpp`).
8. Assert: P2's `sign` returns `SUCCESS`.

This demonstrates that a crafted blob with a valid `x_share` and a mismatched `Q` passes deserialization, enters the protocol, and produces honest-party divergence.

### Citations

**File:** src/cbmpc/api/eddsa2pc.cpp (L18-27)
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

**File:** src/cbmpc/api/eddsa2pc.cpp (L37-43)
```cpp
  if (!q.is_in_range(blob.x_share)) return coinbase::error(E_FORMAT, "invalid key blob");
  key.x_share = blob.x_share;

  error_t rv = key.Q.from_bin(key.curve, blob.Q_compressed);
  if (rv) return coinbase::error(rv, "invalid key blob");
  if (key.curve.check(key.Q)) return coinbase::error(E_FORMAT, "invalid key blob");
  return SUCCESS;
```

**File:** src/cbmpc/api/eddsa2pc.cpp (L210-211)
```cpp
  const auto& G = curve.generator();
  if (x * G != Qi_self) return coinbase::error(E_FORMAT, "x_share mismatch key blob");
```

**File:** src/cbmpc/protocol/schnorr_2p.cpp (L103-110)
```cpp
  std::vector<bn_t> s2(n_sigs);
  if (job.is_p2()) {
    for (int i = 0; i < n_sigs; i++) {
      MODULO(q) s2[i] = e[i] * key.x_share + k2[i];
    }
  }

  if (rv = job.p2_to_p1(s2)) return rv;
```

**File:** src/cbmpc/protocol/schnorr_2p.cpp (L121-124)
```cpp
      if (variant == variant_e::EdDSA) {
        sigs[i] = R[i].to_compressed_bin() + s.to_bin(crypto::ed25519::prv_bin_size()).rev();
        crypto::ecc_pub_key_t pub_key(key.Q);
        if (rv = pub_key.verify(msgs[i], sigs[i])) return coinbase::error(rv, "schnorr_2p: eddsa verify failed");
```

**File:** src/cbmpc/api/eddsa_mp.cpp (L155-158)
```cpp
  const auto& G = curve.generator();
  const auto it_self = Qis.find(blob.party_name);
  if (it_self == Qis.end()) return coinbase::error(E_FORMAT, "invalid key blob");
  if (blob.x_share * G != it_self->second) return coinbase::error(E_FORMAT, "invalid key blob");
```
