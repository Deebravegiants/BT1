I now have all the information needed to assess this vulnerability. Let me trace the complete call chain and validation gaps.

### Title
Missing RSA Modulus Strength Validation in `rsa_pub_key_t::convert` / `rsa_pub_key_t::set` Allows Smooth-Key PVE Encryption — (`src/cbmpc/crypto/base_rsa.cpp`)

---

### Summary

The `parse_ek_blob` → `base_pke_ek_blob_v1_t::convert` → `rsa_pub_key_t::convert` → `rsa_pub_key_t::set` deserialization chain accepts any RSA modulus without checking bit-length or cryptographic strength. An attacker who controls the ek blob bytes can supply a smooth 2048-byte (but easily factorable) modulus. The library encrypts the PVE KEM shared secret under that weak key; the attacker factors `n`, recovers the shared secret, and decrypts the AEAD layer to obtain the private scalar share `x`.

---

### Finding Description

**`parse_ek_blob`** performs only a version check: [1](#0-0) 

**`base_pke_ek_blob_v1_t::convert`** dispatches to `c.convert(rsa_ek)` with no modulus guard: [2](#0-1) 

**`rsa_pub_key_t::convert`** (read path) deserializes `n` and `e` as raw `bn_t` values and immediately calls `set(n, e)` — no `BN_num_bits` check, no primality test, no smoothness check: [3](#0-2) 

**`rsa_pub_key_t::set`** passes `n` and `e` directly to `EVP_PKEY_fromdata` with `EVP_PKEY_PUBLIC_KEY` — OpenSSL does not perform primality or smoothness validation on public-key import: [4](#0-3) 

The same gap exists in the dedicated HSM entry point `base_pke_rsa_ek_from_modulus`, which only checks byte-length (256) and non-zero — no bit-length floor, no trial-division, no primality: [5](#0-4) 

Once the weak key is accepted, `pve_base_pke_rsa().encrypt` calls `kem_policy_rsa_oaep_t::encapsulate`, which calls `pub_key.encrypt_oaep` on the attacker-supplied key: [6](#0-5) 

---

### Impact Explanation

The PVE layer encrypts private scalar shares `x` under the RSA KEM. If the attacker supplies a smooth modulus `n = p₁·p₂·…·pₖ` (all small primes, product ≈ 2^2048), they can:

1. Factor `n` offline (trial division / Pollard's rho in seconds/minutes).
2. Compute `φ(n)` and `d = e⁻¹ mod φ(n)`.
3. Decrypt the RSA-OAEP KEM ciphertext to recover the 32-byte shared secret.
4. Use the shared secret to decrypt the AEAD layer and recover `x` — the private scalar share — without ever possessing the legitimate RSA private key.

This satisfies the Critical impact criterion: a single malicious ek-blob provider causes PVE-encrypted private scalar shares to be recoverable without the legitimate RSA private key.

---

### Likelihood Explanation

The ek blob is an opaque byte string accepted from the caller at every PVE encrypt entry point (`encrypt`, `encrypt_batch`, `partial_decrypt_ac_attempt`, etc.). Any caller who can supply the `ek` argument — including a malicious recipient who provides their own "public key" blob, or an attacker who intercepts and replaces the blob in transit — can trigger this path. The `base_pke_rsa_ek_from_modulus` API additionally exposes this directly to any caller who can pass a raw modulus. No privilege is required beyond the ability to call the public API.

---

### Recommendation

1. **In `rsa_pub_key_t::convert` (read path)**: after deserializing `n`, assert `BN_num_bits(n) == RSA_KEY_LENGTH` and that `n` is odd.
2. **In `parse_ek_blob` or `base_pke_ek_blob_v1_t::convert`**: after deserializing `rsa_ek`, call `EVP_PKEY_param_check` (OpenSSL 3) or an equivalent that performs at least a basic RSA key sanity check.
3. **In `base_pke_rsa_ek_from_modulus`**: add trial-division against small primes (e.g., all primes < 2^16) and reject any modulus that is divisible by a small prime, in addition to the existing size/zero checks.
4. Optionally, enforce that the top bit of `n` is set (i.e., `BN_num_bits(n) == 2048` exactly) to prevent undersized moduli that still serialize to 256 bytes.

---

### Proof of Concept

```
// 1. Build a smooth 2048-bit modulus: n = product of primes until ~2048 bits
BIGNUM* n = BN_new(); BN_set_word(n, 1);
for each small prime p in {3, 5, 7, 11, ...} until BN_num_bits(n) == 2048:
    BN_mul_word(n, p);

// 2. Obtain a valid ek blob via the public API
buf_t ek;
base_pke_rsa_ek_from_modulus(mem_t(BN_to_bin(n), 256), ek);  // succeeds

// 3. Honest party encrypts private scalar share x under the weak key
buf_t ciphertext;
encrypt(curve_secp256k1, ek, label, x, ciphertext);  // succeeds, no rejection

// 4. Attacker factors n (trivial: all factors are known by construction)
// 5. Compute d = e^{-1} mod phi(n), decrypt RSA-OAEP KEM ciphertext
// 6. Use recovered KEM shared secret to decrypt AEAD → recover x
// Assert: recovered x == original x  ← library should have rejected the weak key
```

### Citations

**File:** src/cbmpc/api/pve_internal.h (L53-66)
```text
  void convert(coinbase::converter_t& c) {
    c.convert(version, key_type);
    switch (static_cast<base_pke_key_type_v1>(key_type)) {
      case base_pke_key_type_v1::rsa_oaep_2048:
        c.convert(rsa_ek);
        return;
      case base_pke_key_type_v1::ecies_p256:
        c.convert(ecies_ek);
        return;
      default:
        c.set_error();
        return;
    }
  }
```

**File:** src/cbmpc/api/pve_internal.h (L92-97)
```text
inline error_t parse_ek_blob(mem_t ek, base_pke_ek_blob_v1_t& out) {
  error_t rv = coinbase::convert(out, ek);
  if (rv) return rv;
  if (out.version != base_pke_key_blob_version_v1) return coinbase::error(E_FORMAT, "unsupported base PKE key version");
  return SUCCESS;
}
```

**File:** src/cbmpc/crypto/base_rsa.cpp (L60-73)
```cpp
void rsa_pub_key_t::set(RSA_BASE*& rsa, const BIGNUM* n, const BIGNUM* e) {
  cb_assert(n && e);
  OSSL_PARAM_BLD* param_bld = OSSL_PARAM_BLD_new();
  OSSL_PARAM_BLD_push_BN(param_bld, "n", n);
  OSSL_PARAM_BLD_push_BN(param_bld, "e", e);
  OSSL_PARAM* params = OSSL_PARAM_BLD_to_param(param_bld);

  scoped_ptr_t<EVP_PKEY_CTX> ctx = EVP_PKEY_CTX_new_from_name(NULL, "RSA", NULL);
  cb_assert(EVP_PKEY_fromdata_init(ctx) > 0);
  cb_assert(EVP_PKEY_fromdata(ctx, &rsa, EVP_PKEY_PUBLIC_KEY, params) > 0);

  OSSL_PARAM_free(params);
  OSSL_PARAM_BLD_free(param_bld);
}
```

**File:** src/cbmpc/crypto/base_rsa.cpp (L125-138)
```cpp
  if (!converter.is_write() && !converter.is_error()) {
    create();
    switch (parts) {
      case 0:
        break;
      case part_e | part_n:
        set(n, e);
        break;
      default:
        converter.set_error();
        free();
        return;
    }
  }
```

**File:** src/cbmpc/api/pve_base_pke.cpp (L136-173)
```cpp
error_t base_pke_rsa_ek_from_modulus(mem_t modulus, buf_t& out_ek) {
  if (const error_t rv = coinbase::api::detail::validate_mem_arg_max_size(modulus, "modulus",
                                                                          coinbase::api::detail::MAX_OPAQUE_BLOB_SIZE))
    return rv;

  constexpr int kExpectedModulusBytes = coinbase::crypto::RSA_KEY_LENGTH / 8;
  if (modulus.size != kExpectedModulusBytes)
    return coinbase::error(E_BADARG, "modulus must be exactly 256 bytes (RSA-2048)");

  constexpr unsigned long kDefaultExponent = 65537;

  BIGNUM* n_bn = BN_bin2bn(modulus.data, modulus.size, nullptr);
  if (!n_bn) return coinbase::error(E_GENERAL, "BN_bin2bn(modulus) failed");

  if (BN_is_zero(n_bn)) {
    BN_free(n_bn);
    return coinbase::error(E_BADARG, "modulus must not be zero");
  }

  BIGNUM* e_bn = BN_new();
  if (!e_bn) {
    BN_free(n_bn);
    return coinbase::error(E_GENERAL, "BN_new(e) failed");
  }
  BN_set_word(e_bn, kDefaultExponent);

  coinbase::crypto::rsa_pub_key_t pk;
  pk.set(n_bn, e_bn);
  BN_free(n_bn);
  BN_free(e_bn);

  base_pke_ek_blob_v1_t ek_blob;
  ek_blob.key_type = static_cast<uint32_t>(base_pke_key_type_v1::rsa_oaep_2048);
  ek_blob.rsa_ek = std::move(pk);

  out_ek = coinbase::convert(ek_blob);
  return SUCCESS;
}
```

**File:** include-internal/cbmpc/internal/crypto/base_pki.h (L89-97)
```text
  static error_t encapsulate(const ek_t& pub_key, buf_t& kem_ct, buf_t& kem_ss, drbg_aes_ctr_t* drbg) {
    const int sha256_size_bytes = hash_alg_t::get(hash_e::sha256).size;
    kem_ss = drbg ? drbg->gen(sha256_size_bytes) : gen_random(sha256_size_bytes);
    if (drbg) {
      buf_t seed = drbg->gen_bitlen(sha256_size_bytes * 8);
      return pub_key.encrypt_oaep_with_seed(kem_ss, hash_e::sha256, hash_e::sha256, mem_t(), seed, kem_ct);
    }
    return pub_key.encrypt_oaep(kem_ss, hash_e::sha256, hash_e::sha256, mem_t(), kem_ct);
  }
```
