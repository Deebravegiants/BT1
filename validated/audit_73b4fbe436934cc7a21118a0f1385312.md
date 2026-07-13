### Title
Missing Lower-Half `s` Check in ECDSA Signature Verification Accepts Malleable Signatures - (File: src/cbmpc/crypto/base_ecc.cpp)

### Summary
The `ossl_ecdsa_verify` function in `src/cbmpc/crypto/base_ecc.cpp` validates that `s` is in the range `(0, q)` but does not enforce the lower-half constraint `s ≤ q/2`. This is the direct C++ analog of the reported Solidity bug: a missing upper-bound check on `s` that allows malleable signatures to pass verification through the public `ecc_pub_key_t::verify()` API.

### Finding Description

`ossl_ecdsa_verify` is the core ECDSA verification function used for all non-EdDSA curves. It parses the DER signature, then checks:

```cpp
if (r <= 0 || r >= q || s <= 0 || s >= q)
    return coinbase::error(E_CRYPTO, "ossl_ecdsa_verify: invalid scalar");
``` [1](#0-0) 

This check only enforces `0 < s < q`. It does **not** enforce `s ≤ q/2` (the lower-half constraint). A signature `(r, s)` with `s > q/2` passes this check and proceeds to full ECDSA verification, which will succeed because `(r, s)` and `(r, q-s)` are both mathematically valid ECDSA signatures for the same message and public key.

The call chain from the public API is:

1. `ecc_pub_key_t::verify(mem_t hash, mem_t signature)` — the public verification method [2](#0-1) 

2. Dispatches to `ecurve_secp256k1_t::verify()` for secp256k1: [3](#0-2) 

3. Or to `ecurve_ossl_t::verify()` for P-256/P-384/P-521: [4](#0-3) 

4. Both ultimately call `ossl_ecdsa_verify`, which lacks the lower-S check. [5](#0-4) 

For contrast, the vendored `secp256k1` library's `secp256k1_ecdsa_verify` explicitly enforces lower-S:

```cpp
return (!secp256k1_scalar_is_high(&s) && ...);
``` [6](#0-5) 

The cb-mpc production code does **not** use this vendor function for its own verification path — it uses `ossl_ecdsa_verify` instead, which lacks the equivalent check.

### Impact Explanation

The MPC signing protocols (`ecdsa_2p`, `ecdsa_mp`) do normalize `s` to the lower half before outputting:

```cpp
bn_t q_minus_s = q - s;
if (q_minus_s < s) s = q_minus_s;
``` [7](#0-6) [8](#0-7) 

However, `ecc_pub_key_t::verify()` — the public API used by callers to verify signatures — accepts both `(r, s)` and `(r, q-s)` as valid. An attacker who receives a valid MPC-produced signature can flip `s` to `q-s` and present the malleable variant to any caller using `ecc_pub_key_t::verify()`. The verification will succeed, meaning the library cannot distinguish between the canonical and malleable forms of the same signature.

This is directly reachable through the public API layer (`coinbase::api::ecdsa_2p`, `coinbase::api::ecdsa_mp`) and the C stable ABI (`cbmpc_*`), as callers use `ecc_pub_key_t::verify()` to check returned signatures. [9](#0-8) 

### Likelihood Explanation

Any caller that uses `ecc_pub_key_t::verify()` to validate a signature received from an external source is affected. Since the library is designed for threshold signing of cryptocurrency transactions (Bitcoin, Ethereum), where lower-S is a protocol requirement, this is a realistic attack surface. An attacker who intercepts a valid signature can trivially produce the malleable variant.

### Recommendation

Add a lower-half check for `s` in `ossl_ecdsa_verify`, immediately after the existing range check:

```cpp
if (r <= 0 || r >= q || s <= 0 || s >= q)
    return coinbase::error(E_CRYPTO, "ossl_ecdsa_verify: invalid scalar");
// Add:
bn_t half_q = q >> 1;  // q/2
if (s > half_q)
    return coinbase::error(E_CRYPTO, "ossl_ecdsa_verify: s not in lower half (malleable)");
```

This mirrors the check already present in the vendored `secp256k1` library (`secp256k1_scalar_is_high`) and the recommendation in the original report.

### Proof of Concept

Given a valid DER signature `(r, s)` with `s ≤ q/2` produced by `coinbase::api::ecdsa_2p::sign()`:

1. Parse the DER to extract `r` and `s`.
2. Compute `s' = q - s` (which satisfies `s' > q/2`).
3. Re-encode as DER with `(r, s')`.
4. Call `ecc_pub_key_t::verify(hash, malleable_sig)` — it returns `SUCCESS`.

Both the original and malleable signatures pass `ossl_ecdsa_verify` because the only check is `s < q`, not `s ≤ q/2`. The `ecdsa_signature_t::from_der` parser imposes no lower-S constraint either: [10](#0-9)

### Citations

**File:** src/cbmpc/crypto/base_ecc.cpp (L96-133)
```cpp
error_t ossl_ecdsa_verify(const EC_GROUP* group, EC_POINT* point, mem_t hash, mem_t signature) {
  error_t rv = UNINITIALIZED_ERROR;
  ecurve_t curve = ecurve_t::find(group);
  if (!curve) return coinbase::error(E_CRYPTO, "ossl_ecdsa_verify: unsupported curve");

  ecdsa_signature_t sig;
  if (rv = sig.from_der(curve, signature)) return rv;

  const mod_t& q = curve.order();
  const bn_t& r = sig.get_r();
  const bn_t& s = sig.get_s();
  if (r <= 0 || r >= q || s <= 0 || s >= q) return coinbase::error(E_CRYPTO, "ossl_ecdsa_verify: invalid scalar");

  int curve_size = curve.size();
  if (hash.size >= curve_size) hash.size = curve_size;
  const bn_t e = bn_t::from_bin(hash);

  buf_t oct(curve.point_bin_size());
  cb_assert(EC_POINT_point2oct(group, point, POINT_CONVERSION_UNCOMPRESSED, oct.data(), oct.size(),
                               bn_t::thread_local_storage_bn_ctx()) > 0);

  ecc_point_t Q;
  if (rv = Q.from_oct(curve, oct)) return rv;
  if (rv = curve.check(Q)) return rv;

  bn_t u1, u2;
  MODULO(q) {
    const bn_t w = q.inv(s);
    u1 = e * w;
    u2 = r * w;
  }

  vartime_scope_t vartime_scope;
  const ecc_point_t R = curve.mul_add(u1, Q, u2);
  if (R.is_infinity()) return coinbase::error(E_CRYPTO, "ossl_ecdsa_verify: R is infinity");
  if (q.mod(R.get_x()) != r) return coinbase::error(E_CRYPTO, "ossl_ecdsa_verify: invalid signature");
  return SUCCESS;
}
```

**File:** src/cbmpc/crypto/base_ecc.cpp (L351-352)
```cpp
error_t ecurve_ossl_t::verify(const ecc_pub_key_t& P, mem_t hash, mem_t sig) const {
  return ossl_ecdsa_verify(group, P.ptr, hash, sig);
```

**File:** src/cbmpc/crypto/base_ecc.cpp (L365-365)
```cpp
error_t ecc_pub_key_t::verify(mem_t hash, mem_t signature) const { return curve.ptr->verify(*this, hash, signature); }
```

**File:** src/cbmpc/crypto/base_ecc.cpp (L944-958)
```cpp
error_t ecdsa_signature_t::from_der(ecurve_t curve, mem_t in) {
  const_byte_ptr in_ptr = in.data;
  ECDSA_SIG* sig_ptr = d2i_ECDSA_SIG(NULL, &in_ptr, in.size);
  if (!sig_ptr) return coinbase::error(E_FORMAT);

  const BIGNUM* r_ptr = nullptr;
  const BIGNUM* s_ptr = nullptr;

  ECDSA_SIG_get0(sig_ptr, &r_ptr, &s_ptr);
  r = bn_t(r_ptr);
  s = bn_t(s_ptr);
  ECDSA_SIG_free(sig_ptr);

  this->curve = curve;
  return SUCCESS;
```

**File:** src/cbmpc/crypto/base_ecc_secp256k1.cpp (L342-344)
```cpp
error_t ecurve_secp256k1_t::verify(const ecc_pub_key_t& P, mem_t hash, mem_t sig) const {
  scoped_ptr_t<EC_POINT> point = to_ossl_point(group, P.secp256k1);
  return ossl_ecdsa_verify(group, point, hash, sig);
```

**File:** vendors/secp256k1/src/secp256k1.c (L461-463)
```c
    return (!secp256k1_scalar_is_high(&s) &&
            secp256k1_pubkey_load(ctx, &q, pubkey) &&
            secp256k1_ecdsa_sig_verify(&r, &s, &q, &m));
```

**File:** src/cbmpc/protocol/ecdsa_2p.cpp (L387-388)
```cpp
      bn_t q_minus_s = q - s;
      if (q_minus_s < s) s = q_minus_s;
```

**File:** src/cbmpc/protocol/ecdsa_mp.cpp (L478-479)
```cpp
    bn_t s_reduced = q - s;
    if (s_reduced < s) s = s_reduced;
```

**File:** tests/unit/api/test_ecdsa2pc.cpp (L144-145)
```cpp
  const coinbase::crypto::ecc_pub_key_t verify_key(Q);
  ASSERT_EQ(verify_key.verify(msg_hash, sig1), SUCCESS);
```
