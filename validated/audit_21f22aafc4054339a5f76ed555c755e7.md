Looking at the actual code for `attach_private_scalar` and the related functions to verify the claims.

The code is fully readable. Let me trace the exact validation path carefully.

The code is fully analyzed. Here is my assessment:

---

### Title
Missing stored-anchor cross-check for P2's share in `attach_private_scalar` allows attacker-chosen scalar substitution — (`src/cbmpc/api/ecdsa2pc.cpp`)

### Summary

For P2 (role=1) key blobs, `attach_private_scalar` accepts any attacker-supplied scalar `x'` paired with `Q'=x'*G` without verifying that `Q'` matches the DKG-derived share point. The Paillier binding check that anchors P1's scalar to `c_key` is intentionally skipped for P2, and the `key_blob_v1_t` format stores no P2 public-share point to cross-check against. The result is that a blob with an attacker-chosen `x_share` passes all validation in both `attach_private_scalar` and the subsequent `blob_to_key` / `sign()` path.

### Finding Description

**Blob format — no stored P2 share point.**
`key_blob_v1_t` stores `Q_compressed` (global key), `x_share`, `c_key`, and `paillier`. [1](#0-0) 
It does not store P2's individual public share point `Qi_self = x2*G`. `detach_private_scalar` replaces `x_share` with the out-of-range sentinel `N` and emits no Qi field. [2](#0-1) 

**P1 has a cryptographic anchor; P2 does not.**
For P1 (`paillier_has_private == true`), `attach_private_scalar` decrypts `c_key` and checks `plain == N.mod(x_share)`, binding the scalar to the DKG-produced ciphertext. [3](#0-2) 
For P2 (`paillier_has_private == false`), this block is skipped entirely. [4](#0-3) 

**`public_share_compressed` is only a self-consistency check.**
The sole remaining guard is `x_mod_q * G == Qi_self`, which verifies that the caller-supplied point matches the caller-supplied scalar — a tautology for any attacker who computes `Q' = x'*G`. [5](#0-4) 
Because the blob stores no P2 Qi, there is nothing to compare `public_share_compressed` against.

**`blob_to_key` / `sign()` repeat the same gap.**
`blob_to_key` also skips the Paillier binding for P2 and performs no `x_share * G == Q` check. [6](#0-5) 
The blob with `x_share = x'` therefore passes `deserialize_key_blob` and is handed directly to the signing protocol. [7](#0-6) 

**Contrast with `ecdsa_mp`.**
The multi-party blob stores `Qis_compressed` (a per-party map of compressed share points) and `get_self_Qi_compressed_from_blob` retrieves the stored anchor for cross-checking. [8](#0-7) [9](#0-8) 
The `ecdsa_2p` blob has no equivalent field.

### Impact Explanation

ECDSA-2PC uses additive sharing: `Q = x1*G + x2*G`. [10](#0-9) 
If P2's `x_share` is replaced with attacker-chosen `x'`, the signing protocol runs to completion but produces a signature valid under `Q' = x1*G + x'*G`, not the original `Q`. The blob with the substituted share passes every API-level validation gate and is accepted by `sign()`. The original `Q` is not directly compromised (the attacker cannot forge signatures for `Q`), but the integrity of the restored key material is silently broken: honest code accepts a blob whose P2 share is entirely attacker-controlled, and all subsequent signing output is for a different effective key.

This fits the "High" scope criterion: *attacker-controlled scalars are accepted under the wrong key*.

### Likelihood Explanation

Exploitability requires the attacker to control the `private_scalar` and `public_share_compressed` arguments to `attach_private_scalar`. This is realistic in any backup/restore flow where the scalar is stored externally (e.g., in a backup service or HSM) and the caller computes `public_share_compressed` from the (potentially tampered) scalar at restore time rather than persisting it independently. The API documentation recommends persisting the share point separately, but this is not enforced, and computing it from the scalar at restore time is the natural, obvious implementation choice.

### Recommendation

1. **Store P2's public share point in the blob.** Add a `Qi_self_compressed` field to `key_blob_v1_t` (populated during DKG/refresh serialization) and cross-check `public_share_compressed` against it in `attach_private_scalar`, mirroring the `ecdsa_mp` pattern.
2. **Alternatively**, derive and store `Qi_self` in `detach_private_scalar` so the detached blob carries the anchor, and verify it in `attach_private_scalar`.
3. Elevate the API documentation note to a hard invariant enforced by the implementation.

### Proof of Concept

```
1. Run DKG → obtain p2_blob (role=1).
2. Call detach_private_scalar(p2_blob) → (pub_blob, original_scalar).
3. Generate fresh random scalar x_prime; compute Q_prime = x_prime * G.
4. Call attach_private_scalar(pub_blob, x_prime, Q_prime) → assert SUCCESS.
5. Call sign(job, restored_blob, msg_hash) → assert SUCCESS.
6. Verify the returned signature against the original Q → FAILS.
   Verify against Q_prime = x1*G + x_prime*G → SUCCEEDS (if x1 is known).
```

Steps 4 and 5 both succeed because `attach_private_scalar` has no stored anchor to reject `x_prime`, and `blob_to_key` repeats the same gap. Step 6 demonstrates that the accepted blob silently encodes a different effective key.

### Citations

**File:** src/cbmpc/api/ecdsa2pc.cpp (L21-32)
```cpp
struct key_blob_v1_t {
  uint32_t version = key_blob_version_v1;
  uint32_t role = 0;   // 0=p1, 1=p2
  uint32_t curve = 0;  // coinbase::api::curve_id

  buf_t Q_compressed;
  coinbase::crypto::bn_t x_share;
  coinbase::crypto::bn_t c_key;
  coinbase::crypto::paillier_t paillier;

  void convert(coinbase::converter_t& c) { c.convert(version, role, curve, Q_compressed, x_share, c_key, paillier); }
};
```

**File:** src/cbmpc/api/ecdsa2pc.cpp (L72-75)
```cpp
  if (paillier_has_private) {
    const coinbase::crypto::bn_t plain = blob.paillier.decrypt(blob.c_key);
    if (plain != N.mod(blob.x_share)) return coinbase::error(E_FORMAT, "invalid key blob");
  }
```

**File:** src/cbmpc/api/ecdsa2pc.cpp (L166-176)
```cpp
  coinbase::mpc::ecdsa2pc::key_t key;
  error_t rv = deserialize_key_blob(key_blob, key);
  if (rv) return rv;

  const auto self = to_internal_party(job.self);
  if (key.role != self) return coinbase::error(E_BADARG, "job.self mismatch key blob role");

  coinbase::mpc::job_2p_t mpc_job = to_internal_job(job);

  sig_der.free();
  return fn(mpc_job, sid, key, msg_hash, sig_der);
```

**File:** src/cbmpc/api/ecdsa2pc.cpp (L225-232)
```cpp
  key_blob_v1_t pub;
  pub.role = static_cast<uint32_t>(key.role);
  pub.curve = static_cast<uint32_t>(cid);
  pub.Q_compressed = key.Q.to_compressed_bin();
  pub.x_share = key.paillier.get_N().value();  // x_share == N is out of range
  pub.c_key = key.c_key;
  pub.paillier = key.paillier;
  out_public_key_blob = coinbase::convert(pub);
```

**File:** src/cbmpc/api/ecdsa2pc.cpp (L258-259)
```cpp
  const bool paillier_has_private = pub.paillier.has_private_key();
  if ((pub.role == 0) != paillier_has_private) return coinbase::error(E_FORMAT, "invalid key blob");
```

**File:** src/cbmpc/api/ecdsa2pc.cpp (L273-278)
```cpp
  // If we have the private key (P1), bind the share to its Paillier encryption.
  if (paillier_has_private) {
    coinbase::crypto::vartime_scope_t vartime_scope;
    const coinbase::crypto::bn_t plain = pub.paillier.decrypt(pub.c_key);
    if (plain != N.mod(x_share)) return coinbase::error(E_FORMAT, "x_share mismatch key blob");
  }
```

**File:** src/cbmpc/api/ecdsa2pc.cpp (L285-289)
```cpp
  coinbase::crypto::ecc_point_t Qi_self(curve);
  if (rv = Qi_self.from_bin(curve, public_share_compressed))
    return coinbase::error(rv, "invalid public_share_compressed");
  if (rv = curve.check(Qi_self)) return coinbase::error(rv, "invalid public_share_compressed");
  if (x_mod_q * curve.generator() != Qi_self) return coinbase::error(E_FORMAT, "x_share mismatch key blob");
```

**File:** src/cbmpc/api/ecdsa_mp.cpp (L27-41)
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

**File:** src/cbmpc/api/ecdsa_mp.cpp (L64-71)
```cpp
static error_t get_self_Qi_compressed_from_blob(const key_blob_v1_t& blob, buf_t& out_Qi_self_compressed) {
  if (blob.party_name.empty()) return coinbase::error(E_FORMAT, "invalid key blob");
  const auto it = blob.Qis_compressed.find(blob.party_name);
  if (it == blob.Qis_compressed.end()) return coinbase::error(E_FORMAT, "invalid key blob");
  if (it->second.empty()) return coinbase::error(E_FORMAT, "invalid key blob");
  out_Qi_self_compressed = it->second;
  return SUCCESS;
}
```

**File:** tests/unit/protocol/test_ecdsa_2p.cpp (L22-22)
```cpp
    EXPECT_EQ(k1.x_share * G + k2.x_share * G, k1.Q);
```
