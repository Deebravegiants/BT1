### Title
Missing Key-State Binding in Threshold Refresh Consistency Check Allows Silent Divergence of Key Shares — (`src/cbmpc/protocol/ec_dkg.cpp`)

### Summary

The `dkg_or_refresh_ac` function, which implements the threshold/access-structure key refresh for all multi-party protocols (ECDSA-MP, Schnorr-MP, EdDSA-MP), omits the current key state from its inter-party consistency hash. The additive `refresh` path explicitly binds the consistency check to `(sid, current_key.Q, current_key.Qis)`, preventing parties with stale or mismatched key blobs from silently diverging. The threshold refresh path hashes only `(curve_name, all_pids, quorum_pids, sid)`. A malicious peer that deliberately presents a stale key blob — or an honest party that restores from an old backup — can complete the refresh protocol without any error, but each party will compute a different new key share. The resulting shares are cryptographically inconsistent: they do not form a valid secret sharing of the original key, so all subsequent signing operations silently produce invalid signatures or fail.

### Finding Description

**Root cause — additive refresh vs. threshold refresh consistency hash:**

The additive `key_share_mp_t::refresh` binds the consistency check to the current key state:

```cpp
h_consistency._i = crypto::sha256_t::hash(sid, current_key.Q, current_key.Qis);
``` [1](#0-0) 

The threshold `dkg_or_refresh_ac` (called for every `refresh_ac` invocation) only hashes protocol parameters:

```cpp
h_consistency._i = crypto::sha256_t::hash(std::string(curve.get_name()), all_pids, quorum_pids, sid);
``` [2](#0-1) 

**Why the final integrity check does not catch the divergence:**

After the refresh, the code verifies:

```cpp
if (reconstructed_Q != key.Q) return coinbase::error(E_CRYPTO, "key.Q mismatch");
``` [3](#0-2) 

The refresh adds zero-sum randomness: `reconstruct_exponent(delta_Qis) = 0`. Therefore `reconstruct_exponent(key_stale.Qis + delta_Qis) = Q` and `reconstruct_exponent(key_current.Qis + delta_Qis) = Q` both equal the original `Q`. The check passes for every party regardless of which starting key they used.

**Exploit path:**

1. All n parties run `dkg_ac` → each obtains a valid AC key blob (version `ac_key_blob_version_v1`).
2. Honest parties run `refresh_ac` (round 1). Party P_m participates and receives a new key blob, but retains the old one.
3. Honest parties run `refresh_ac` (round 2). P_m deliberately supplies the old key blob from step 1.
4. The `h_consistency` broadcast check passes for all parties (it does not cover key state).
5. Each party computes `new_key.x_share = key_i.x_share + x_i` where `key_i` differs between P_m (old) and honest parties (current). The resulting shares are inconsistent.
6. The protocol returns `SUCCESS` on all parties with no error.

**Public API entry path:**

`coinbase::api::ecdsa_mp::refresh_ac` → `deserialize_ac_key_blob` → `coinbase::mpc::ecdsampc::refresh_ac` → `eckey::key_share_mp_t::refresh_ac` → `dkg_or_refresh_ac(is_refresh=true)` [4](#0-3) [5](#0-4) 

The same path exists for `schnorr_mp::refresh_ac` and `eddsa_mp::refresh_ac`. [6](#0-5) [7](#0-6) 

### Impact Explanation

After the corrupted refresh, all parties hold key shares that do not form a valid secret sharing of the original key. Every subsequent `sign_ac` call will either fail with a cryptographic error or produce a signature that fails external verification. The original key is effectively destroyed — recovery requires a fresh DKG, losing the original key material. This constitutes honest-party divergence, unsafe state acceptance (the protocol accepts an inconsistent starting state without error), and invalid cryptographic output with security impact.

### Likelihood Explanation

The attack requires a malicious party that is a member of the full party set (`job.party_names`) for the refresh. This is a reachable role in any deployment that uses threshold key management. The malicious party needs only to retain an old key blob and present it during a subsequent refresh — no privileged access, no cryptographic break, and no external infrastructure is required. The library explicitly does not authenticate or encrypt key blobs at rest, so a party can freely choose which blob to present.

### Recommendation

When `is_refresh = true`, include the current key state in the consistency hash, mirroring the additive refresh:

```cpp
// In dkg_or_refresh_ac, when is_refresh == true:
h_consistency._i = crypto::sha256_t::hash(
    std::string(curve.get_name()), all_pids, quorum_pids, sid,
    key.Q, key.Qis   // <-- add these
);
```

This ensures that any party presenting a stale or mismatched key blob will produce a different `h_consistency` value, causing the broadcast check to abort the protocol before any shares are computed.

### Proof of Concept

```
Setup (n=3, threshold=2-of-3, parties p0, p1, p2):

1. dkg_ac(p0,p1,p2) → key_v1 for each party.
2. refresh_ac(p0,p1,p2) → key_v2 for each party.
   p2 retains key_v1 (simulating stale blob / old backup).
3. refresh_ac(p0,p1,p2):
   - p0, p1 supply key_v2 blobs.
   - p2 supplies key_v1 blob.
   h_consistency for all = SHA256(curve, pids, sid) — identical, check passes.
   Protocol completes with SUCCESS on all parties.
4. p0.new_x = key_v2_p0.x_share + x_i_p0
   p2.new_x = key_v1_p2.x_share + x_i_p2   ← different starting point
   The three new shares are not a valid 2-of-3 sharing of the original key.
5. sign_ac(p0, p1) → invalid signature (verifier rejects) or protocol error.
   The key is permanently corrupted; a fresh DKG is required.
```

### Citations

**File:** src/cbmpc/protocol/ec_dkg.cpp (L188-189)
```cpp
  auto h_consistency = job.uniform_msg<buf256_t>();
  h_consistency._i = crypto::sha256_t::hash(sid, current_key.Q, current_key.Qis);
```

**File:** src/cbmpc/protocol/ec_dkg.cpp (L302-303)
```cpp
  auto h_consistency = job.uniform_msg<buf256_t>();
  h_consistency._i = crypto::sha256_t::hash(std::string(curve.get_name()), all_pids, quorum_pids, sid);
```

**File:** src/cbmpc/protocol/ec_dkg.cpp (L446-448)
```cpp
    if (rv = ac.reconstruct_exponent(new_key.Qis, reconstructed_Q))
      return coinbase::error(rv, "Failed to reconstruct exponent for new_key");
    if (reconstructed_Q != key.Q) return coinbase::error(E_CRYPTO, "key.Q mismatch");
```

**File:** src/cbmpc/protocol/ec_dkg.cpp (L470-474)
```cpp
error_t key_share_mp_t::refresh_ac(job_mp_t& job, const ecurve_t& curve, buf_t& sid, const crypto::ss::ac_t ac,
                                   const party_set_t& quorum_party_set, key_share_mp_t& key, key_share_mp_t& new_key) {
  bool is_refresh = true;
  return dkg_or_refresh_ac(job, curve, sid, ac, quorum_party_set, key, new_key, is_refresh);
}
```

**File:** src/cbmpc/api/ecdsa_mp.cpp (L329-356)
```cpp
  coinbase::mpc::ecdsampc::key_t key;
  key_blob.free();

  rv = coinbase::mpc::ecdsampc::dkg_ac(mpc_job, icurve, sid, ac, quorum_party_set, key);
  if (rv) return rv;

  return serialize_ac_key_blob(job, key, key_blob);
}

error_t refresh_additive(const job_mp_t& job, buf_t& sid, mem_t key_blob, buf_t& new_key_blob) {
  error_t rv = validate_job_mp(job);
  if (rv) return rv;
  if (rv = coinbase::api::detail::validate_mem_arg_max_size(key_blob, "key_blob",
                                                            coinbase::api::detail::MAX_OPAQUE_BLOB_SIZE))
    return rv;

  coinbase::mpc::ecdsampc::key_t key;
  rv = deserialize_key_blob(job, key_blob, key);
  if (rv) return rv;

  coinbase::mpc::job_mp_t mpc_job = to_internal_job(job);

  coinbase::mpc::ecdsampc::key_t new_key;
  new_key_blob.free();
  rv = coinbase::mpc::ecdsampc::refresh(mpc_job, sid, key, new_key);
  if (rv) return rv;

  return serialize_key_blob(job, new_key, new_key_blob);
```

**File:** src/cbmpc/api/schnorr_mp.cpp (L326-355)
```cpp
error_t refresh_ac(const coinbase::api::job_mp_t& job, buf_t& sid, mem_t key_blob,
                   const access_structure_t& access_structure, const std::vector<std::string_view>& quorum_party_names,
                   buf_t& new_key_blob) {
  error_t rv = validate_job_mp(job);
  if (rv) return rv;
  if (rv = coinbase::api::detail::validate_mem_arg_max_size(key_blob, "key_blob",
                                                            coinbase::api::detail::MAX_OPAQUE_BLOB_SIZE))
    return rv;

  coinbase::mpc::schnorrmp::key_t key;
  rv = deserialize_ac_key_blob(job, key_blob, key);
  if (rv) return rv;

  coinbase::crypto::ss::ac_owned_t ac;
  rv = coinbase::api::detail::to_internal_access_structure(access_structure, job.party_names, key.curve, ac);
  if (rv) return rv;

  coinbase::mpc::party_set_t quorum_party_set;
  rv = coinbase::api::detail::to_internal_party_set(job.party_names, quorum_party_names, quorum_party_set);
  if (rv) return rv;

  coinbase::mpc::job_mp_t mpc_job = to_internal_job(job);

  coinbase::mpc::schnorrmp::key_t new_key;
  new_key_blob.free();
  rv = coinbase::mpc::schnorrmp::refresh_ac(mpc_job, key.curve, sid, ac, quorum_party_set, key, new_key);
  if (rv) return rv;

  return serialize_ac_key_blob(job, new_key, new_key_blob);
}
```

**File:** src/cbmpc/api/eddsa_mp.cpp (L329-356)
```cpp
error_t refresh_ac(const job_mp_t& job, buf_t& sid, mem_t key_blob, const access_structure_t& access_structure,
                   const std::vector<std::string_view>& quorum_party_names, buf_t& new_key_blob) {
  error_t rv = validate_job_mp(job);
  if (rv) return rv;
  if (rv = coinbase::api::detail::validate_mem_arg_max_size(key_blob, "key_blob",
                                                            coinbase::api::detail::MAX_OPAQUE_BLOB_SIZE))
    return rv;

  coinbase::mpc::schnorrmp::key_t key;
  rv = deserialize_ac_key_blob(job, key_blob, key);
  if (rv) return rv;

  coinbase::crypto::ss::ac_owned_t ac;
  rv = coinbase::api::detail::to_internal_access_structure(access_structure, job.party_names, key.curve, ac);
  if (rv) return rv;

  coinbase::mpc::party_set_t quorum_party_set;
  rv = coinbase::api::detail::to_internal_party_set(job.party_names, quorum_party_names, quorum_party_set);
  if (rv) return rv;

  coinbase::mpc::job_mp_t mpc_job = to_internal_job(job);

  coinbase::mpc::schnorrmp::key_t new_key;
  new_key_blob.free();
  rv = coinbase::mpc::schnorrmp::refresh_ac(mpc_job, key.curve, sid, ac, quorum_party_set, key, new_key);
  if (rv) return rv;

  return serialize_ac_key_blob(job, new_key, new_key_blob);
```
