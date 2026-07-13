The vulnerability is real. Here is the complete analysis:

---

### Title
2-Party Schnorr Refresh Accepts Cross-Session Key Blobs Without Q Consistency Verification — (`src/cbmpc/protocol/ec_dkg.cpp`)

### Summary
`key_share_2p_t::refresh` copies `Q` from each party's local blob without any cross-party exchange or verification that both parties hold the same public key. A Byzantine P2 supplying a blob from a different DKG session causes both parties to complete refresh with `SUCCESS`, leaving P1 holding a new blob whose `Q` is inconsistent with P2's new blob. The honest P1 accepts the refreshed blob as valid and, if it replaces the original, loses the ability to sign under the original key.

### Finding Description

The call chain is:

`cbmpc_schnorr_2p_refresh` → `coinbase::api::schnorr_2p::refresh` → `key_share_2p_t::refresh`

In `src/cbmpc/c_api/schnorr2pc.cpp`, `cbmpc_schnorr_2p_refresh` validates only that the job struct is well-formed and the key blob is non-empty, then delegates to the API layer. [1](#0-0) 

In `src/cbmpc/api/schnorr2pc.cpp`, `refresh` deserializes the caller's own blob, checks that the role field matches `job.self`, and calls the protocol layer. No Q value is exchanged with the peer at this layer. [2](#0-1) 

In `src/cbmpc/protocol/ec_dkg.cpp`, `key_share_2p_t::refresh` does the following:

```cpp
new_key.Q = key.Q;   // line 95: Q copied from local blob only
```

Then it calls `agree_random`, which exchanges only fresh random bits — it has no input binding to `Q`, `x_share`, or any session identifier derived from the key. [3](#0-2) 

`agree_random` itself is a pure coin-flip: P1 commits to `r1`, P2 sends `r2`, output is `r1 XOR r2`. No key material is included in the transcript. [4](#0-3) 

**The missing guard:** there is no step where either party broadcasts `Q` (or a hash of it) and verifies the peer's value matches. Compare to `key_share_mp_t::refresh`, which explicitly hashes `sid, current_key.Q, current_key.Qis` into `h_consistency`, broadcasts it, and verifies agreement before proceeding — and then re-checks `SUM(new_key.Qis) == current_key.Q` at the end: [5](#0-4) [6](#0-5) 

The 2-party path has neither check.

### Impact Explanation

With P1 holding blob A `(x1_A, Q_A)` and Byzantine P2 supplying blob B `(x2_B, Q_B)` where `Q_A ≠ Q_B`:

- Both parties call `agree_random` and obtain the same `r`.
- P1 writes `new_key = { x_share: x1_A + r, Q: Q_A }` — `SUCCESS`.
- P2 writes `new_key = { x_share: x2_B − r, Q: Q_B }` — `SUCCESS`.

Both refreshed blobs are accepted without error. P1's new blob encodes `Q_A`; P2's new blob encodes `Q_B`. The actual combined scalar is `x1_A + x2_B`, which corresponds to neither `Q_A` nor `Q_B`. Any subsequent signing session will either fail or produce a signature that verifies under no known public key. If P1 discards the pre-refresh blob (the expected operational pattern), P1's key share is permanently destroyed.

This fits the **High** impact category: attacker-controlled blob data (from a different DKG session) is accepted under the wrong key, causing honest-party divergence and unsafe state acceptance.

### Likelihood Explanation

The attacker is Byzantine P2 — a legitimate protocol participant who controls their own key blob input. No threshold collusion is required; P2 alone can trigger this by simply providing a blob from any other DKG session. The API imposes no cross-party Q binding at any layer. The attack requires only that P2 possess two valid key blobs (one from each session), which is a normal operational state.

### Recommendation

Before the `agree_random` call in `key_share_2p_t::refresh`, both parties should exchange and verify a commitment to their local `Q`. The simplest fix mirrors what `key_share_mp_t::refresh` already does: include `Q` (and optionally a session identifier) in the `agree_random` transcript, or add an explicit committed broadcast of `hash(Q)` with cross-party equality check before any randomness is consumed. The refresh should abort with `E_CRYPTO` if the peer's committed `Q` does not match the local `Q`.

### Proof of Concept

```
// Session A DKG: P1 gets (x1_A, Q_A), P2_honest gets (x2_A, Q_A)
// Session B DKG: P1_honest gets (x1_B, Q_B), P2_attacker gets (x2_B, Q_B)

// Refresh run:
//   P1 supplies blob_A = {x1_A, Q_A, role=P1}
//   P2 (Byzantine) supplies blob_B = {x2_B, Q_B, role=P2}

// agree_random produces shared r (no Q binding)
// P1 new blob: {x1_A + r, Q_A}  -- returned SUCCESS
// P2 new blob: {x2_B - r, Q_B}  -- returned SUCCESS

// Assert: new_blob_P1.Q != new_blob_P2.Q  --> TRUE (Q_A != Q_B)
// Assert: (x1_A + r + x2_B - r) * G == Q_A  --> FALSE
// Assert: (x1_A + r + x2_B - r) * G == Q_B  --> FALSE
// Signing with these blobs produces no valid signature under any known Q.
```

### Citations

**File:** src/cbmpc/c_api/schnorr2pc.cpp (L46-72)
```cpp
cbmpc_error_t cbmpc_schnorr_2p_refresh(const cbmpc_2pc_job_t* job, cmem_t key_blob, cmem_t* out_new_key_blob) {
  try {
    if (!out_new_key_blob) return E_BADARG;
    *out_new_key_blob = cmem_t{nullptr, 0};
    const auto vjob = validate_2pc_job(job);
    if (vjob) return vjob;
    const auto vkb = validate_cmem(key_blob);
    if (vkb) return vkb;

    coinbase::api::party_2p_t self_cpp;
    const auto pconv = to_cpp_party(job->self, self_cpp);
    if (pconv) return pconv;

    job_2p_cpp_ctx_t ctx(job, self_cpp);
    coinbase::buf_t new_key;
    const coinbase::error_t rv = coinbase::api::schnorr_2p::refresh(ctx.job, view_cmem(key_blob), new_key);
    if (rv) return rv;

    return alloc_cmem_from_buf(new_key, out_new_key_blob);
  } catch (const std::bad_alloc&) {
    if (out_new_key_blob) *out_new_key_blob = cmem_t{nullptr, 0};
    return E_INSUFFICIENT;
  } catch (...) {
    if (out_new_key_blob) *out_new_key_blob = cmem_t{nullptr, 0};
    return E_GENERAL;
  }
}
```

**File:** src/cbmpc/api/schnorr2pc.cpp (L79-99)
```cpp
error_t refresh(const coinbase::api::job_2p_t& job, mem_t key_blob, buf_t& new_key_blob) {
  if (const error_t rv = validate_job_2p(job)) return rv;
  if (const error_t rv = coinbase::api::detail::validate_mem_arg_max_size(key_blob, "key_blob",
                                                                          coinbase::api::detail::MAX_OPAQUE_BLOB_SIZE))
    return rv;
  coinbase::mpc::schnorr2p::key_t key;
  error_t rv = deserialize_key_blob(key_blob, key);
  if (rv) return rv;

  const auto self = to_internal_party(job.self);
  if (key.role != self) return coinbase::error(E_BADARG, "job.self mismatch key blob role");

  coinbase::mpc::job_2p_t mpc_job = to_internal_job(job);

  coinbase::mpc::schnorr2p::key_t new_key;
  new_key_blob.free();
  rv = coinbase::mpc::eckey::key_share_2p_t::refresh(mpc_job, key, new_key);
  if (rv) return rv;

  return serialize_key_blob(new_key, new_key_blob);
}
```

**File:** src/cbmpc/protocol/ec_dkg.cpp (L91-111)
```cpp
error_t key_share_2p_t::refresh(job_2p_t& job, const key_share_2p_t& key, key_share_2p_t& new_key) {
  error_t rv = UNINITIALIZED_ERROR;
  new_key.role = key.role;
  new_key.curve = key.curve;
  new_key.Q = key.Q;

  const mod_t& q = key.curve.order();
  buf_t rand_bits;
  if (rv = agree_random(job, q.get_bits_count() + SEC_P_STAT, rand_bits)) return rv;
  bn_t r = bn_t::from_bin(rand_bits) % q;

  if (job.is_p1()) {
    MODULO(q) { new_key.x_share = key.x_share + r; }
  }

  if (job.is_p2()) {
    MODULO(q) { new_key.x_share = key.x_share - r; }
  }

  return SUCCESS;
}
```

**File:** src/cbmpc/protocol/ec_dkg.cpp (L188-213)
```cpp
  auto h_consistency = job.uniform_msg<buf256_t>();
  h_consistency._i = crypto::sha256_t::hash(sid, current_key.Q, current_key.Qis);

  new_key = current_key;

  auto r = job.nonuniform_msg<bn_t>();
  auto R = job.uniform_msg<std::vector<ecc_point_t>>(std::vector<ecc_point_t>(n));
  auto pi_r = job.uniform_msg<std::vector<zk::uc_dl_t>>(std::vector<zk::uc_dl_t>(n));
  for (int j = 0; j < n; j++) {
    r._ij = bn_t::rand(q);
    R._i[j] = r._ij * G;
    pi_r._i[j].prove(R._i[j], r._ij, sid, i * n + j);
  }

  crypto::commitment_t com_R(sid, pid);
  auto c = job.uniform_msg<buf256_t>();
  auto rho = job.uniform_msg<buf256_t>();
  com_R.gen(R.msg, pi_r.msg);
  c._i = com_R.msg;     // c_i
  rho._i = com_R.rand;  // rho_i
  if (rv = job.plain_broadcast(c, h_consistency)) return rv;

  for (int j = 0; j < n; j++) {
    if (j == i) continue;
    if (h_consistency._j != h_consistency) return coinbase::error(E_CRYPTO);
  }
```

**File:** src/cbmpc/protocol/ec_dkg.cpp (L258-261)
```cpp
  if (new_key.Qis[job.get_name(i)] != new_key.x_share * G) return coinbase::error(E_CRYPTO);

  if (SUM(new_key.Qis) != current_key.Q) return coinbase::error(E_CRYPTO);
  new_key.Q = current_key.Q;
```

**File:** src/cbmpc/protocol/agree_random.cpp (L7-36)
```cpp
error_t agree_random(job_2p_t& job, int bitlen, buf_t& out) {
  error_t rv = UNINITIALIZED_ERROR;
  buf_t r1, r2;
  const crypto::mpc_pid_t& sender_pid = job.get_pid(party_t::p1);
  coinbase::crypto::commitment_t com(sender_pid);

  if (job.is_p1()) {
    r1 = crypto::gen_random_bitlen(bitlen);
    com.gen(r1);
  }

  if (rv = job.p1_to_p2(com.msg)) return rv;

  if (job.is_p2()) {
    r2 = crypto::gen_random_bitlen(bitlen);
  }

  if (rv = job.p2_to_p1(r2)) return rv;
  if (rv = job.p1_to_p2(r1, com.rand)) return rv;

  if (job.is_p2()) {
    if (rv = com.open(r1)) return rv;
  }

  if (r1.size() != coinbase::bits_to_bytes(bitlen)) return coinbase::error(E_CRYPTO);
  if (r2.size() != coinbase::bits_to_bytes(bitlen)) return coinbase::error(E_CRYPTO);

  out = mem_t(r1) ^ mem_t(r2);
  return SUCCESS;
}
```
