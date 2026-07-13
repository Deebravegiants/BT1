### Title
ECDSA-2PC `detach_private_scalar` Retains Paillier Private Key in "Public" Blob, Enabling Recovery of P1's Key Share — (`File: src/cbmpc/api/ecdsa2pc.cpp`)

---

### Summary

`coinbase::api::ecdsa_2p::detach_private_scalar` is the public API for splitting P1's ECDSA-2PC key blob into a "public" blob (intended for less-secure storage) and a detached private scalar (for HSM/secure storage). However, the produced `out_public_key_blob` retains the full Paillier private key (`p`, `q`) for P1. Because the blob also retains `c_key = Enc_Paillier(x_share)`, any party that obtains the "public" blob can decrypt `c_key` and recover P1's ECDSA private key share `x_share` in full.

---

### Finding Description

The ECDSA-2PC key blob structure is defined in the anonymous namespace of `src/cbmpc/api/ecdsa2pc.cpp`:

```cpp
struct key_blob_v1_t {
  uint32_t version, role, curve;
  buf_t Q_compressed;
  coinbase::crypto::bn_t x_share;
  coinbase::crypto::bn_t c_key;       // Enc_Paillier(x_share)
  coinbase::crypto::paillier_t paillier; // has_private=true for P1 (contains p, q)
  void convert(coinbase::converter_t& c) { c.convert(version, role, curve, Q_compressed, x_share, c_key, paillier); }
};
``` [1](#0-0) 

The protocol invariant (enforced in `blob_to_key`) is that P1 (role=0) always holds the Paillier private key:

```cpp
const bool paillier_has_private = blob.paillier.has_private_key();
if ((blob.role == 0) != paillier_has_private) return coinbase::error(E_FORMAT, "invalid key blob");
``` [2](#0-1) 

`detach_private_scalar` replaces `x_share` with an out-of-range sentinel but copies the full `paillier` object (including `p`, `q`) verbatim into the output "public" blob:

```cpp
key_blob_v1_t pub;
pub.x_share = key.paillier.get_N().value();  // sentinel: out of range
pub.c_key   = key.c_key;
pub.paillier = key.paillier;                 // ← full private key (p, q) retained
out_public_key_blob = coinbase::convert(pub);
``` [3](#0-2) 

`paillier_t::convert` serializes `p` and `q` whenever `has_private` is true:

```cpp
void paillier_t::convert(coinbase::converter_t& converter) {
  converter.convert(has_private);
  converter.convert(N);
  if (has_private) {
    converter.convert(p);
    converter.convert(q);
  }
  ...
}
``` [4](#0-3) 

Therefore the serialized `out_public_key_blob` for P1 contains `(N, p, q, c_key)`. Since `c_key = Enc_Paillier(x_share)`, decrypting `c_key` with the embedded private key directly yields `x_share`.

The public C API wrapper `cbmpc_ecdsa_2p_detach_private_scalar` exposes the same path: [5](#0-4) 

The API header names the output `out_public_key_blob` and gives no warning that it still contains the Paillier private key: [6](#0-5) 

By contrast, the ECDSA-MP variant explicitly states "The public blob is safe to persist as public-only material": [7](#0-6) 

---

### Impact Explanation

An attacker who obtains the `out_public_key_blob` for P1 (e.g., from a database where the caller stored it believing it was "public") can:

1. Deserialize the blob using the library's documented format to extract `(N, p, q, c_key)`.
2. Call `paillier_t::decrypt(c_key)` with the embedded private key to recover `x_share mod N`.
3. Reduce `x_share mod q` to obtain P1's ECDSA private key share.

With P1's key share, the attacker can combine it with P2's share (obtained through a separate compromise or by acting as P2) to reconstruct the full ECDSA private key and forge arbitrary signatures — or, if acting as a malicious P2, use the recovered share to complete signing without P1's participation.

This satisfies the Critical impact criterion: a shipped public API path lets an attacker recover a private scalar (key share) from material that the API's naming and design imply is safe to store with reduced protection.

---

### Likelihood Explanation

The `detach_private_scalar` / `attach_private_scalar` pattern is the library's documented mechanism for PVE-based backup workflows (demonstrated in `demo-api/ecdsa_mp_pve_backup/main.cpp`). A caller following the natural usage pattern — store `out_public_key_blob` in a database, store `out_private_scalar` in an HSM — would expose the Paillier private key to any party with database read access. The function name and output parameter name (`out_public_key_blob`) provide no indication that the blob remains secret-bearing.

---

### Recommendation

**Short term:** In `detach_private_scalar` for ECDSA-2PC, strip the Paillier private key from the output blob. Replace:
```cpp
pub.paillier = key.paillier;
```
with a version that copies only the public modulus `N`:
```cpp
pub.paillier.create_pub(key.paillier.get_N().value());
```

**Long term:** Update `attach_private_scalar` to remove the Paillier-decryption consistency check (which requires the private key). The existing `(x mod q)*G == Qi_self` check is sufficient to bind the scalar to the blob. Add an explicit documentation note to the ECDSA-2PC `detach_private_scalar` header mirroring the ECDSA-MP wording, and add a test asserting that the output blob does not deserialize a Paillier private key.

---

### Proof of Concept

```cpp
// Step 1: P1 performs DKG and calls detach_private_scalar for backup.
buf_t p1_key_blob;
coinbase::api::ecdsa_2p::dkg(job1, curve_id::secp256k1, p1_key_blob);

buf_t public_blob, private_scalar;
coinbase::api::ecdsa_2p::detach_private_scalar(p1_key_blob, public_blob, private_scalar);
// Caller stores public_blob in a database (believing it is "public").
// Caller stores private_scalar in an HSM.

// Step 2: Attacker reads public_blob from the database.
// Deserialize using the library's internal format (open source):
coinbase::api::ecdsa_2p::key_blob_v1_t blob;  // accessible via source
coinbase::convert(blob, public_blob);

// blob.paillier.has_private_key() == true  (p, q are present)
// blob.c_key == Enc_Paillier(x_share)

// Step 3: Attacker decrypts c_key to recover x_share.
coinbase::crypto::bn_t recovered = blob.paillier.decrypt(blob.c_key);
// recovered == x_share mod N  (P1's full ECDSA private key share)
// Reduce mod q to get the signing scalar.
```

The `key_blob_v1_t` struct is in an anonymous namespace but the library is open source; an attacker can replicate the deserialization trivially. The `paillier_t::decrypt` path is confirmed reachable and correct for a 2048-bit private key. [8](#0-7) [9](#0-8)

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

**File:** src/cbmpc/api/ecdsa2pc.cpp (L49-50)
```cpp
  const bool paillier_has_private = blob.paillier.has_private_key();
  if ((blob.role == 0) != paillier_has_private) return coinbase::error(E_FORMAT, "invalid key blob");
```

**File:** src/cbmpc/api/ecdsa2pc.cpp (L208-234)
```cpp
error_t detach_private_scalar(mem_t key_blob, buf_t& out_public_key_blob, buf_t& out_private_scalar) {
  if (const error_t rv = coinbase::api::detail::validate_mem_arg_max_size(key_blob, "key_blob",
                                                                          coinbase::api::detail::MAX_OPAQUE_BLOB_SIZE))
    return rv;
  coinbase::mpc::ecdsa2pc::key_t key;
  error_t rv = deserialize_key_blob(key_blob, key);
  if (rv) return rv;

  curve_id cid;
  if (!from_internal_curve(key.curve, cid)) return coinbase::error(E_BADARG, "unsupported curve");
  if (cid == curve_id::ed25519) return coinbase::error(E_BADARG, "unsupported curve");

  // Variable-length big-endian encoding (may grow after refresh).
  out_private_scalar = key.x_share.to_bin();

  // Produce a v1-format blob with an invalid (out-of-range) scalar share so it is
  // rejected by sign/refresh APIs.
  key_blob_v1_t pub;
  pub.role = static_cast<uint32_t>(key.role);
  pub.curve = static_cast<uint32_t>(cid);
  pub.Q_compressed = key.Q.to_compressed_bin();
  pub.x_share = key.paillier.get_N().value();  // x_share == N is out of range
  pub.c_key = key.c_key;
  pub.paillier = key.paillier;
  out_public_key_blob = coinbase::convert(pub);
  return SUCCESS;
}
```

**File:** src/cbmpc/crypto/base_paillier.cpp (L15-21)
```cpp
void paillier_t::convert(coinbase::converter_t& converter) {
  converter.convert(has_private);
  converter.convert(N);
  if (has_private) {
    converter.convert(p);
    converter.convert(q);
  }
```

**File:** src/cbmpc/crypto/base_paillier.cpp (L239-288)
```cpp
bn_t paillier_t::decrypt(const bn_t& src) const {
  cb_assert(src > 0 && src < NN && "paillier_t::decrypt: src must be in (0, N^2)");
  cb_assert(mod_t::coprime(src, N) && "paillier_t::decrypt: src must be coprime with N");
  bn_t c1;

  if (has_private) {
    c1 = crt_dec.compute_power(src, NN);
  } else {
    cb_assert(false);
  }

  // Side-channel note:
  // This is the Paillier L(u) step: L(c1) = (c1 - 1) / N, with c1 ∈ Z_{N^2}.
  // For odd N, division by N can be replaced by multiplication with N^{-1} modulo 2^k:
  //   (c1 - 1) = N * L(c1)  ⇒  L(c1) ≡ (c1 - 1) * N^{-1} (mod 2^k)
  // With k = 2048 and 0 ≤ L(c1) < N < 2^k, this recovers L(c1) exactly from the low k bits.
  constexpr int BN_ULONG_BITS = int(sizeof(BN_ULONG) * 8);
  static_assert(bit_size % BN_ULONG_BITS == 0, "Paillier bit_size must be BN_ULONG-word aligned");
  constexpr int k_words = bit_size / BN_ULONG_BITS;

  const BIGNUM& c1_bn = *(const BIGNUM*)c1;
  cb_assert(c1_bn.top >= 0);

  // tmp_low = (c1 - 1) mod 2^k (little-endian words)
  BN_ULONG tmp_low[k_words];
  BN_ULONG borrow = 1;
  for (int i = 0; i < k_words; i++) {
    BN_ULONG w = 0;
    if (i < c1_bn.top) w = c1_bn.d[i];
    tmp_low[i] = w - borrow;
    borrow = (borrow && (w == 0)) ? 1 : 0;
  }

  // m1_words = tmp_low * inv_N_mod_2k mod 2^k
  const BIGNUM& inv_bn = *(const BIGNUM*)inv_N_mod_2k;
  cb_assert(inv_bn.top == k_words);
  BN_ULONG prod[k_words * 2];
  bn_mul_normal(prod, tmp_low, k_words, inv_bn.d, k_words);

  bn_t m1;
  BIGNUM& m1_bn = *(BIGNUM*)m1;
  cb_assert(bn_wexpand(&m1_bn, k_words));
  std::copy(prod, prod + k_words, m1_bn.d);
  m1_bn.top = k_words;
  m1_bn.neg = 0;
  m1_bn.flags |= BN_FLG_FIXED_TOP | BN_FLG_CONSTTIME;

  MODULO(N) m1 *= inv_phi_N;
  return m1;
}
```

**File:** src/cbmpc/c_api/ecdsa2pc.cpp (L189-202)
```cpp
cbmpc_error_t cbmpc_ecdsa_2p_detach_private_scalar(cmem_t key_blob, cmem_t* out_public_key_blob,
                                                   cmem_t* out_private_scalar) {
  try {
    if (!out_public_key_blob || !out_private_scalar) return E_BADARG;
    *out_public_key_blob = cmem_t{nullptr, 0};
    *out_private_scalar = cmem_t{nullptr, 0};
    const auto vkb = validate_cmem(key_blob);
    if (vkb) return vkb;

    coinbase::buf_t public_blob;
    coinbase::buf_t private_scalar;
    const coinbase::error_t rv =
        coinbase::api::ecdsa_2p::detach_private_scalar(view_cmem(key_blob), public_blob, private_scalar);
    if (rv) return rv;
```

**File:** include/cbmpc/api/ecdsa_2p.h (L54-65)
```text
// Detach the private scalar share from a key blob, producing:
// - a key blob with its private scalar removed, and
// - the private scalar x encoded as a big-endian buffer.
//
// The scalar-removed blob is not usable for signing/refresh until restored with
// `attach_private_scalar`.
//
// Note (ECDSA-2PC encoding):
// - Unlike ECDSA-MP, this scalar encoding is NOT fixed-length. ECDSA-2PC keeps
//   the share as a Paillier-compatible integer representative and it may grow
//   after refresh.
error_t detach_private_scalar(mem_t key_blob, buf_t& out_public_key_blob, buf_t& out_private_scalar);
```

**File:** include/cbmpc/api/ecdsa_mp.h (L101-111)
```text
// Detach the private scalar share from a key blob, producing:
// - a "public" key blob with its private scalar wiped, and
// - the private scalar x encoded as a fixed-length big-endian buffer.
//
// The public blob is safe to persist as public-only material, but is not usable
// for signing/refresh until restored with `attach_private_scalar`.
//
// Output:
// - `out_private_scalar_fixed` length equals the curve order size in bytes
//   (e.g., 32 bytes for secp256k1/p256).
error_t detach_private_scalar(mem_t key_blob, buf_t& out_public_key_blob, buf_t& out_private_scalar_fixed);
```
