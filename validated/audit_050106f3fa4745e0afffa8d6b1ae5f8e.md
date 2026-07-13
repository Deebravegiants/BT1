I need to trace the full path carefully: `cbmpc_schnorr_mp_sign_ac` → `sign_ac` → `to_additive_share` → `reconstruct_additive_share` THRESHOLD case, checking every guard along the way.

### Title
Missing DKG-time threshold validation in `sign_ac` produces accepted-invalid BIP340 signatures — (`src/cbmpc/api/schnorr_mp.cpp`, `src/cbmpc/protocol/ec_dkg.cpp`)

---

### Summary

`cbmpc_schnorr_mp_sign_ac` accepts any structurally valid access structure whose leaf set matches the key's party set. It does not verify that the threshold value matches the one used at DKG time. Passing THRESHOLD[k'] with k' < k causes `to_additive_share` → `reconstruct_additive_share` to apply Lagrange interpolation with the wrong number of PIDs, producing raw polynomial evaluations instead of correctly-weighted additive shares. The internal consistency invariant `x_share * G == Qi_self` still holds (because `reconstruct_pub_additive_shares` applies the same wrong interpolation), so no error is returned. The signing protocol completes with `SUCCESS` and emits a 64-byte signature that fails BIP340 verification against the actual public key.

---

### Finding Description

**Entry point**: `cbmpc_schnorr_mp_sign_ac` → `coinbase::api::schnorr_mp::sign_ac` [1](#0-0) 

**Validation performed by `to_internal_access_structure`**: [2](#0-1) 

The function validates:
1. Shape constraints (threshold_k ≥ 1, threshold_k ≤ children.size())
2. Leaf set equals the key's party set exactly
3. Tree structural validity via `validate_tree()`

It does **not** validate that `threshold_k` matches the value used during DKG. THRESHOLD[1](p0,p1,p2) passes all checks when the key was generated with THRESHOLD[2](p0,p1,p2).

**`to_additive_share` guard**: [3](#0-2) 

`ac.enough_for_quorum({p0,p1})` with THRESHOLD[1] returns `true` (count=1 ≥ threshold=1), so no error.

**`reconstruct_additive_share` THRESHOLD case** with k'=1 and quorum {p0,p1}: [4](#0-3) 

- `node->threshold` = 1 (from the caller-supplied structure)
- Only the first satisfied child (p0) is selected into `interp_pids`
- `lagrange_partial_interpolate(0, {x_share_p0}, {pid_p0}, [pid_p0], q)` is called with a single-element `all_pids`
- With one PID, the Lagrange basis evaluates to 1, so the result is `x_share_p0` — the raw polynomial evaluation, not the correctly-weighted additive share [5](#0-4) 

**`reconstruct_pub_additive_shares` THRESHOLD case** applies the identical single-PID interpolation in the exponent: [6](#0-5) 

This yields `new_Qis[p0] = Qis[p0]` (the original stored public share point). Since `x_share_p0 * G = Qis[p0]` was verified at DKG time, the invariant `new_x_share * G == new_Qis[party_name]` holds. No error is returned.

**Mathematical consequence**: For a THRESHOLD[2] DKG, shares lie on a degree-1 polynomial f(t) = x + a·t. The correct additive shares for quorum {p0,p1} are f(pid_p0)·λ_p0 and f(pid_p1)·λ_p1 (Lagrange coefficients), which sum to x. The wrong additive shares are f(pid_p0) and f(pid_p1) (raw evaluations), which sum to 2x + a·(pid_p0 + pid_p1) ≠ x. The signing protocol runs on these wrong shares and produces a signature for the wrong key, which fails BIP340 verification against Q. [7](#0-6) 

---

### Impact Explanation

The API returns `SUCCESS` with a 64-byte signature that fails external BIP340 verification. No error code is surfaced to the caller. Any downstream system that trusts the `SUCCESS` return code and uses the signature will encounter a verification failure. This is accepted invalid cryptographic output from a public API reachable validation bypass in signing.

This does **not** allow key recovery, private scalar extraction, or forgery of a valid signature for the real key Q. The impact is correctness/reliability: the signing protocol silently produces an invalid result.

---

### Likelihood Explanation

The attack requires only that the caller pass a structurally valid access structure with the same leaf set but a smaller threshold. This is a single integer change in the `cbmpc_access_structure_node_t.threshold_k` field. No cryptographic material or protocol interaction is needed beyond what a legitimate signing participant already has. The path is fully reachable from the public C API.

---

### Recommendation

Store the original access structure (or at minimum the threshold value at each node) in the AC key blob at DKG/refresh time, and validate at `sign_ac` time that the caller-supplied structure's threshold values match. Alternatively, document explicitly that the access structure passed to `sign_ac` must be identical to the one used at DKG/refresh time, and add a structural equality check (not just leaf-set equality) in `to_internal_access_structure` when called from signing paths.

---

### Proof of Concept

```
1. Run dkg_ac with THRESHOLD[2](p0, p1, p2), quorum {p0, p1}.
   → Each party holds x_share_pi = f(pid_pi) for degree-1 polynomial f with f(0)=x.

2. Call sign_ac on each party with THRESHOLD[1](p0, p1, p2) and signing quorum {p0, p1}.
   → to_internal_access_structure: leaf set {p0,p1,p2} matches, threshold_k=1 ≥ 1, passes.
   → enough_for_quorum({p0,p1}) with THRESHOLD[1]: count=1 ≥ 1, passes.
   → reconstruct_additive_share: interp_pids=[pid_p0], Lagrange basis=1,
     new_x_share_p0 = x_share_p0 (raw eval).
   → reconstruct_pub_additive_shares: new_Qis[p0] = Qis[p0].
   → x_share_p0 * G == Qis[p0]: consistency holds, SUCCESS returned.
   → Signing runs on wrong additive shares; signature produced.

3. Assert bip340::verify(Q, msg, sig) == FAILURE.
   → sum of wrong additive shares = x_share_p0 + x_share_p1
     = (x + a*pid_p0) + (x + a*pid_p1) ≠ x mod q.
   → Signature is for the wrong key; verification fails.
```

### Citations

**File:** src/cbmpc/api/schnorr_mp.cpp (L357-404)
```cpp
error_t sign_ac(const coinbase::api::job_mp_t& job, mem_t ac_key_blob, const access_structure_t& access_structure,
                mem_t msg, party_idx_t sig_receiver, buf_t& sig) {
  error_t rv = validate_job_mp(job);
  if (rv) return rv;
  if (rv = coinbase::api::detail::validate_mem_arg_max_size(ac_key_blob, "ac_key_blob",
                                                            coinbase::api::detail::MAX_OPAQUE_BLOB_SIZE))
    return rv;
  if (rv = coinbase::api::detail::validate_mem_arg(msg, "msg")) return rv;
  if (msg.size != 32) return coinbase::error(E_BADARG, "BIP340 requires a 32-byte message");
  if (sig_receiver < 0 || static_cast<size_t>(sig_receiver) >= job.party_names.size())
    return coinbase::error(E_BADARG, "invalid sig_receiver");

  coinbase::mpc::schnorrmp::key_t ac_key;
  rv = deserialize_ac_key_blob(ac_key_blob, ac_key);
  if (rv) return rv;

  // Bind the key share to the local party identity in the job.
  const std::string_view self_name_sv(job.party_names[static_cast<size_t>(job.self)]);
  if (ac_key.party_name != self_name_sv) return coinbase::error(E_BADARG, "job.self mismatch key blob");

  // Full party set is the key's Qis key set.
  std::vector<std::string_view> all_party_names;
  all_party_names.reserve(ac_key.Qis.size());
  for (const auto& kv : ac_key.Qis) all_party_names.emplace_back(kv.first);

  // Validate that the signing party set (`job.party_names`) is a subset of the key's party set.
  coinbase::mpc::party_set_t _unused;
  rv = coinbase::api::detail::to_internal_party_set(all_party_names, job.party_names, _unused);
  if (rv) return rv;

  // Convert access structure to internal and validate it matches the key party set.
  coinbase::crypto::ss::ac_owned_t ac;
  rv = coinbase::api::detail::to_internal_access_structure(access_structure, all_party_names, ac_key.curve, ac);
  if (rv) return rv;

  // Convert signing party list to internal set of names.
  std::set<coinbase::crypto::pname_t> quorum_names;
  for (const auto& name : job.party_names) quorum_names.insert(std::string(name));

  coinbase::mpc::schnorrmp::key_t additive_key;
  rv = ac_key.to_additive_share(ac, quorum_names, additive_key);
  if (rv) return rv;

  coinbase::mpc::job_mp_t mpc_job = to_internal_job(job);

  sig.free();
  return coinbase::mpc::schnorrmp::sign(mpc_job, additive_key, msg, sig_receiver, sig,
                                        coinbase::mpc::schnorrmp::variant_e::BIP340);
```

**File:** src/cbmpc/api/access_structure_util.h (L157-205)
```text
inline error_t to_internal_access_structure(const access_structure_t& in,
                                            const std::vector<std::string_view>& party_names,
                                            coinbase::crypto::ecurve_t curve, coinbase::crypto::ss::ac_owned_t& out) {
  // Clear any existing tree.
  delete out.root;
  out.root = nullptr;

  if (!curve.valid()) return coinbase::error(E_BADARG, "access_structure: invalid curve");

  // Basic shape validation (independent of job).
  error_t rv = validate_access_structure_node(in);
  if (rv) return rv;
  if (in.type == access_structure_t::node_type::leaf)
    return coinbase::error(E_BADARG, "access_structure: root cannot be leaf");

  // Validate that leaf set matches job.party_names exactly.
  std::set<std::string> leaf_names;
  rv = collect_leaf_names(in, leaf_names);
  if (rv) return rv;

  std::set<std::string> party_set;
  for (const auto& name_view : party_names) party_set.insert(std::string(name_view));

  if (leaf_names != party_set)
    return coinbase::error(E_BADARG, "access_structure: leaf names must match job.party_names exactly");

  // Build internal node tree with generated internal node names.
  std::unordered_set<std::string> used;
  used.reserve(leaf_names.size() * 2 + 8);
  used.insert(std::string());  // root name
  for (const auto& name : leaf_names) used.insert(name);

  uint64_t counter = 0;
  coinbase::crypto::ss::node_t* root = nullptr;
  rv = build_internal_ac_node(in, /*depth=*/0, /*is_root=*/true, used, counter, root);
  if (rv) return rv;

  out.curve = curve;
  out.root = root;

  rv = out.validate_tree();
  if (rv) {
    delete out.root;
    out.root = nullptr;
    return rv;
  }

  return SUCCESS;
}
```

**File:** src/cbmpc/protocol/ec_dkg.cpp (L530-575)
```cpp
    case node_e::THRESHOLD: {
      std::vector<bn_t> interp_pids;
      interp_pids.reserve(node->threshold);
      bn_t share = 0;
      bn_t share_pid = 0;
      int satisfied_count = 0;

      for (int i = 0; i < n; i++) {
        bn_t share_from_child;
        bool child_is_satisfied = false;
        rv = reconstruct_additive_share(q, node->children[i], quorum_names, share_from_child, child_is_satisfied);
        if (rv == E_INSUFFICIENT) {
          continue;
        }
        if (rv) return rv;

        if (!child_is_satisfied) continue;

        satisfied_count++;
        const bn_t child_pid = node->children[i]->get_pid();
        const bool child_is_selected = int(interp_pids.size()) < node->threshold;
        if (!child_is_selected) continue;

        interp_pids.push_back(child_pid);
        if (share_from_child != 0) {
          share_pid = child_pid;
          share = share_from_child;
        }
      }

      if (satisfied_count < node->threshold) {
        dylog_disable_scope_t dylog_disable_scope;
        return coinbase::error(E_INSUFFICIENT);
      }
      is_satisfied = true;

      // Target party is outside the selected quorum subtree for this threshold node.
      if (share_pid == 0) {
        additive_share = 0;
        break;
      }

      cb_assert(int(interp_pids.size()) == node->threshold);

      additive_share = crypto::lagrange_partial_interpolate(0, {share}, {share_pid}, interp_pids, q);
    } break;
```

**File:** src/cbmpc/protocol/ec_dkg.cpp (L640-686)
```cpp
    case node_e::THRESHOLD: {
      std::vector<bn_t> interp_pids;
      interp_pids.reserve(node->threshold);
      ecc_point_t share = curve.infinity();
      bn_t share_pid = 0;
      int satisfied_count = 0;

      for (int i = 0; i < n; i++) {
        ecc_point_t share_from_child = curve.infinity();
        bool child_is_satisfied = false;
        rv = reconstruct_pub_additive_shares(node->children[i], quorum_names, target, share_from_child,
                                             child_is_satisfied);
        if (rv == E_INSUFFICIENT) {
          continue;
        }
        if (rv) return rv;

        if (!child_is_satisfied) continue;

        satisfied_count++;
        const bn_t child_pid = node->children[i]->get_pid();
        const bool child_is_selected = int(interp_pids.size()) < node->threshold;
        if (!child_is_selected) continue;

        interp_pids.push_back(child_pid);
        if (!share_from_child.is_infinity()) {
          share_pid = child_pid;
          share = share_from_child;
        }
      }

      if (satisfied_count < node->threshold) {
        dylog_disable_scope_t dylog_disable_scope;
        return coinbase::error(E_INSUFFICIENT);
      }
      is_satisfied = true;

      // Target party is outside the selected quorum subtree for this threshold node.
      if (share_pid == 0) {
        pub_additive_shares = curve.infinity();
        break;
      }

      cb_assert(int(interp_pids.size()) == node->threshold);

      pub_additive_shares = crypto::lagrange_partial_interpolate_exponent(0, {share}, {share_pid}, interp_pids);
    } break;
```

**File:** src/cbmpc/protocol/ec_dkg.cpp (L695-704)
```cpp
error_t key_share_mp_t::to_additive_share(const crypto::ss::ac_t ac, const std::set<crypto::pname_t>& quorum_names,
                                          key_share_mp_t& additive_share) {
  if (!ac.enough_for_quorum(quorum_names)) {
    return coinbase::error(E_INSUFFICIENT);
  }
  error_t rv = UNINITIALIZED_ERROR;
  const mod_t& q = curve.order();
  bn_t new_x_share;
  bool _ignore_is_satisfied = false;
  if (rv = reconstruct_additive_share(q, ac.root, quorum_names, new_x_share, _ignore_is_satisfied)) return rv;
```

**File:** src/cbmpc/protocol/ec_dkg.cpp (L718-724)
```cpp
  additive_share.x_share = new_x_share;
  additive_share.Q = Q;
  additive_share.Qis = new_Qis;
  additive_share.curve = curve;
  additive_share.party_name = party_name;

  return SUCCESS;
```

**File:** src/cbmpc/crypto/lagrange.cpp (L88-102)
```cpp
bn_t lagrange_partial_interpolate(const bn_t& x, const std::vector<bn_t>& shares,
                                  const std::vector<bn_t>& pids_for_shares, const std::vector<bn_t>& all_pids,
                                  const mod_t& q) {
  cb_assert(pids_for_shares.size() == shares.size() && "shares and pids_for_shares must have the same size");
  cb_assert(all_pids.size() >= shares.size() && "all_pids must have at least as many elements as shares");
  int m = (int)shares.size();
  bn_t secret = 0;

  for (int i = 0; i < m; i++) {
    bn_t lambda = lagrange_basis(x, all_pids, pids_for_shares[i], q);
    MODULO(q) secret += lambda * shares[i];
  }

  return secret;
}
```
