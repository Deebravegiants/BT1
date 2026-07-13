Now I have all the information needed for a complete analysis. Let me trace the full path.

**Key facts established:**

1. **`key_share_mp_t::dkg`** — no explicit expected-curve check on `Qi._j` before ZK verify: [1](#0-0) 

2. **`uc_dl_t::verify`** — infers curve from the received point itself, then checks the point is on *that* curve (not the expected protocol curve): [2](#0-1) 

3. **`ecurve_t::check`** — the check at line 594 only validates that the point's embedded curve tag matches `*this`; when called as `curve.check(Q)` inside `uc_dl_t::verify`, `curve` was derived from `Q.get_curve()`, so it is trivially self-consistent for any well-formed point on any curve: [3](#0-2) 

4. **`sign_batch`** — correctly does `curve.check(point)` using the *expected* `curve` from `key.curve` before calling `pi._j.verify`, which is the guard that `dkg` is missing: [4](#0-3) 

5. **`ecc_point_t::add`** — uses `cb_assert` (not a returning error) for curve mismatch, meaning in release builds this is typically a no-op, allowing cross-curve addition to proceed with undefined/garbage behavior: [5](#0-4) 

6. **`h_consistency`** — only ensures all parties agree on the curve *name string*; it does not validate that the received `Qi._j` point is actually on that curve: [6](#0-5) 

---

### Title
Missing Expected-Curve Validation of Peer Public Key Share `Qi._j` Before ZK Proof Verification in `key_share_mp_t::dkg` — (`src/cbmpc/protocol/ec_dkg.cpp`)

### Summary
A Byzantine peer can broadcast a public key share `Qi._j` on a different elliptic curve (e.g., ed25519 in a secp256k1 DKG session) along with a ZK proof valid for that wrong curve. Because `uc_dl_t::verify` infers the curve from the received point itself rather than from the expected protocol curve, the ZK proof passes. The misleading comment at line 157 ("curve check of Qi._j is done inside the zk verify function") is factually incorrect for cross-curve attacks. The DKG then stores the wrong-curve point in `key.Qis` and proceeds to `SUM(key.Qis)`, where a `cb_assert`-only curve mismatch guard (not a returning error) means release builds may silently produce garbage or undefined-behavior output.

### Finding Description

**Attack path:**

1. Byzantine party B participates in a secp256k1 DKG session.
2. Round 1: B sends the correct `h_consistency = SHA256("secp256k1")`, passing the curve-name agreement check at line 137.
3. Round 2: B broadcasts `Qi._j` as a valid ed25519 point and `pi._j` as a valid `uc_dl_t` proof for that ed25519 point.
4. Honest party A calls `pi._j.verify(Qi._j, sid, j)` (line 158).
5. Inside `uc_dl_t::verify`: `curve = Qi._j.get_curve()` → ed25519; `curve.check(Qi._j)` passes (ed25519 point is on ed25519); `G = curve.generator()` → ed25519 generator; the Fischlin check `A_sum == z_sum * G - e_sum * Q` is verified against ed25519 arithmetic. Since B crafted a valid ed25519 proof, this returns `SUCCESS`.
6. `key.Qis[job.get_name(j)] = Qi._j` stores the ed25519 point.
7. `key.Q = SUM(key.Qis)` calls `ecc_point_t::add` on points from different curves. The only guard is `cb_assert(val1.curve == val2.curve)`, which is a no-op in release builds, leading to undefined behavior or a garbage `key.Q`.

**Why the existing guards are insufficient:**

- `h_consistency` (line 123/137): Checks that all parties agree on the curve name string. B sends the correct secp256k1 name hash. This does not validate the curve of the received point.
- `uc_dl_t::verify` curve check (line 66): `curve.check(Q)` where `curve = Q.get_curve()`. This is a self-referential check — it verifies the point is on its own embedded curve, not on the expected protocol curve.
- The commitment opening (line 155): Verifies that `Qi._j` matches what B committed to in round 1. B committed to the ed25519 point, so this passes.

**Contrast with `sign_batch`:** The signing protocol correctly calls `curve.check(point)` using the expected `curve` from `key.curve` (line 108) before calling `pi._j.verify`. This guard is absent in `dkg`. [4](#0-3) [7](#0-6) 

### Impact Explanation
An honest party completes DKG with `key.Qis` containing a point on the wrong curve and `key.Q` computed via undefined cross-curve arithmetic. This is an accepted invalid cryptographic output: the DKG key material is structurally corrupt. Any subsequent protocol (signing, refresh) that relies on `key.Q` or `key.Qis` operates on garbage public data, potentially enabling signature forgery or key substitution depending on how the garbage value interacts with downstream operations.

### Likelihood Explanation
Any single Byzantine participant in an n-party DKG can trigger this. No threshold collusion is required. The attacker only needs to craft a valid ZK proof for a point on a different curve, which is straightforward since they control the witness.

### Recommendation
Add an explicit expected-curve check on `Qi._j` before calling `pi._j.verify`, mirroring the pattern already used in `sign_batch`:

```cpp
// In key_share_mp_t::dkg, replace:
// curve check of Qi._j is done inside the zk verify function
if (rv = pi._j.verify(Qi._j, sid, j)) return rv;

// With:
if (rv = curve.check(Qi._j)) return coinbase::error(rv, "dkg: Qi._j is not on the expected curve");
if (rv = pi._j.verify(Qi._j, sid, j)) return rv;
```

The same pattern should be audited in `key_share_mp_t::refresh` (line 231) and `dkg_or_refresh_ac` (line 391), where similar comments ("Curve check of R._j[l] is done inside the zk verify function" / "Verifying that R values are on the curve and subgroup is done in the zk verify function") indicate the same incorrect assumption. [8](#0-7) [9](#0-8) 

### Proof of Concept

```cpp
// In a secp256k1 DKG session, Byzantine party B does:
ecurve_t wrong_curve = crypto::curve_ed25519;
bn_t w = bn_t::rand(wrong_curve.order());
ecc_point_t Qi_malicious = w * wrong_curve.generator();  // ed25519 point

zk::uc_dl_t pi_malicious;
pi_malicious.prove(Qi_malicious, w, sid, j);  // valid proof for ed25519

// B broadcasts Qi_malicious and pi_malicious in round 2.
// On the honest party's side:
error_t rv = pi_malicious.verify(Qi_malicious, sid, j);
// rv == SUCCESS  <-- ZK proof passes against ed25519 generator
// Expected: rv != SUCCESS (E_CRYPTO), because Qi_malicious is not on secp256k1
```

The assertion `rv == SUCCESS` demonstrates that `uc_dl_t::verify` accepts a proof for a point on the wrong curve, confirming the guard is absent.

### Citations

**File:** src/cbmpc/protocol/ec_dkg.cpp (L122-138)
```cpp
  auto h_consistency = job.uniform_msg<buf256_t>();
  h_consistency._i = crypto::sha256_t::hash(std::string(curve.get_name()));

  auto sid_i = job.uniform_msg<buf_t>(crypto::gen_random_bitlen(SEC_P_COM));
  key.x_share = bn_t::rand(q);
  auto Qi = job.uniform_msg<ecc_point_t>(key.x_share * G);

  coinbase::crypto::commitment_t com(sid_i, job.get_pid(i));

  com.gen(Qi.msg);
  auto c = job.uniform_msg<buf_t>(com.msg);
  if (rv = job.plain_broadcast(sid_i, c, h_consistency)) return rv;

  for (int j = 0; j < n; j++) {
    if (j == i) continue;
    if (h_consistency._j != h_consistency) return coinbase::error(E_CRYPTO);
  }
```

**File:** src/cbmpc/protocol/ec_dkg.cpp (L149-165)
```cpp
  for (int j = 0; j < n; j++) {
    if (j == i) continue;

    if (sid_msg._j != sid) return coinbase::error(E_CRYPTO);
    if (h._j != h.msg) return coinbase::error(E_CRYPTO);

    if (rv = crypto::commitment_t(sid_i._j, job.get_pid(j)).set(rho._j, c._j).open(Qi._j)) return rv;

    // curve check of Qi._j is done inside the zk verify function
    if (rv = pi._j.verify(Qi._j, sid, j)) return rv;
  }

  for (int j = 0; j < n; j++) {
    key.Qis[job.get_name(j)] = Qi._j;
  }
  key.Q = SUM(key.Qis);
  return SUCCESS;
```

**File:** src/cbmpc/protocol/ec_dkg.cpp (L219-232)
```cpp
  for (int j = 0; j < n; j++) {
    if (j == i) continue;

    // Curve check of R._j[l] is done inside the zk verify function further below

    if (h._j != h) return coinbase::error(E_CRYPTO);
    if (R._j.size() != size_t(n)) return coinbase::error(E_CRYPTO, "ec_dkg: inconsistent batch size (R)");
    if (pi_r._j.size() != size_t(n)) return coinbase::error(E_CRYPTO, "ec_dkg: inconsistent batch size (pi_r)");

    if (rv = com_R.id(sid, job.get_pid(j)).set(rho._j, c._j).open(R._j, pi_r._j)) return rv;
    for (int l = 0; l < n; l++) {
      if (l == j) continue;
      if (rv = pi_r._j[l].verify(R._j[l], sid, j * n + l)) return rv;
    }
```

**File:** src/cbmpc/protocol/ec_dkg.cpp (L388-392)
```cpp

    cs[j] = c_all._j;
    // Verifying that R values are on the curve and subgroup is done in the zk verify function
    if (rv = pi_r_all._j.verify(Rs, sid, j)) return coinbase::error(rv, "Failed to verify pi_r_all");
    if (is_refresh) {
```

**File:** src/cbmpc/zk/zk_ec.cpp (L64-71)
```cpp
  ecurve_t curve = Q.get_curve();
  const mod_t& q = curve.order();
  if (rv = curve.check(Q)) return coinbase::error(rv, "uc_dl_t::verify: Q is not on the curve");
  for (int i = 0; i < rho; i++) {
    if (rv = curve.check(A[i])) return coinbase::error(rv, "uc_dl_t::verify: A[i] is not on the curve");
  }

  const auto& G = curve.generator();
```

**File:** src/cbmpc/crypto/base_ecc.cpp (L592-601)
```cpp
error_t ecurve_t::check(const ecc_point_t& point) const {
  if (!point.valid()) return crypto::error("EC-point invalid");
  if (point.get_curve() != *this) return crypto::error("EC-point of wrong curve");
  if (!point.is_in_subgroup()) return crypto::error("EC-point is not on curve");

  if (!thread_local_store_allow_ecc_infinity) {
    if (point.is_infinity()) return crypto::error("EC-point is infinity");
  }
  return SUCCESS;
}
```

**File:** src/cbmpc/crypto/base_ecc.cpp (L817-823)
```cpp
ecc_point_t ecc_point_t::add(const ecc_point_t& val1, const ecc_point_t& val2)  // static
{
  cb_assert(val1.curve == val2.curve && "ecc_point_t::add: curve mismatch");
  ecc_point_t result(val1.curve);
  val1.curve.ptr->add(val1, val2, result);
  return result;
}
```

**File:** src/cbmpc/protocol/schnorr_mp.cpp (L107-110)
```cpp
    for (const auto& point : Ri._j) {
      if (rv = curve.check(point)) return coinbase::error(rv, "schnorr_mp_t::sign_batch: check Ri failed");
    }
    if (rv = pi._j.verify(Ri._j, sid._i, j)) return coinbase::error(rv, "schnorr_mp_t::sign_batch: verify pi failed");
```
