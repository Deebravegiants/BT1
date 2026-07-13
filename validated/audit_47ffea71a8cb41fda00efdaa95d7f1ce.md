### Title
Missing Minimum KEM Shared-Secret Length Guard in `kem_encap_shim` / `kem_policy_runtime_kem_t` Allows Trivially Weak PVE Ciphertext - (`src/cbmpc/c_api/pve_base_pke.cpp`)

---

### Summary

`cbmpc_pve_encrypt_with_kem` accepts a caller-supplied `cbmpc_pve_kem_encap_fn` callback. The shim that bridges the C callback into the C++ KEM layer (`kem_encap_shim`) validates only that `kem_ss.size >= 0` and that a non-zero size has a non-null pointer. It imposes **no minimum length** on the returned KEM shared secret. The value flows directly into `kem_aead_ciphertext_t::seal` as HKDF-Extract IKM with no further length check, so a 1-byte KEM SS produces a 256-key AES-GCM-256 DEM key. The function returns `CBMPC_SUCCESS` and a structurally valid ciphertext with 8 bits of effective security.

---

### Finding Description

**Call chain:**

```
cbmpc_pve_encrypt_with_kem          (pve_base_pke.cpp:315)
  → coinbase::api::pve::encrypt(adapter, ...)
      → c_base_kem_adapter_t::encrypt
          → pve_base_pke_runtime_kem().encrypt(pve_keyref(ek_i), ...)
              → kem_pve_base_pke_t<kem_policy_runtime_kem_t>::encrypt
                  → kem_aead_ciphertext_t<kem_policy_runtime_kem_t>::seal
                      → kem_policy_runtime_kem_t::encapsulate
                          → kem_encap_shim  (pve_base_pke.cpp:20)
                              → user cbmpc_pve_kem_encap_fn callback
```

**The guard in `kem_encap_shim`:** [1](#0-0) 

```cpp
if (kem_ss.size < 0 || (kem_ss.size > 0 && !kem_ss.data)) {
    ...
    return E_FORMAT;
}
out_kem_ss = coinbase::buf_t(kem_ss.data, kem_ss.size);
```

A callback returning `{ptr, 1}` (1-byte SS) passes both conditions and is accepted without error.

**The HKDF step in `kem_aead_ciphertext_t::seal`:** [2](#0-1) 

```cpp
buf_t prk = crypto::hkdf_extract_sha256(mem_t(), kem_ss);
buf_t aes_key = crypto::hkdf_expand_sha256(prk, mem_t("CBMPC|KEM-AEAD|v1|..."), 32);
crypto::aes_gcm_t::encrypt(aes_key, mem_t(iv, iv_size), aad, tag_size, plain, aead_ciphertext);
```

`kem_ss` is used as the sole IKM with no length check. A 1-byte IKM means the PRK has only 8 bits of entropy, and the derived 256-bit AES key is drawn from a space of 256 values.

**Contrast with the RSA-OAEP HSM path**, which explicitly enforces a 32-byte minimum: [3](#0-2) 

```cpp
const int expected_ss_size = crypto::hash_alg_t::get(crypto::hash_e::sha256).size;
if (kem_ss.size() != expected_ss_size) return coinbase::error(E_CRYPTO, "invalid RSA KEM output size");
```

The runtime KEM path (`kem_policy_runtime_kem_t`) has no equivalent check. [4](#0-3) 

---

### Impact Explanation

A malicious or buggy `cbmpc_pve_kem_encap_fn` callback returning a 1-byte KEM SS causes `cbmpc_pve_encrypt_with_kem` to return `CBMPC_SUCCESS` with a structurally valid PVE ciphertext whose AES-GCM-256 DEM key is drawn from a space of at most 256 values. An attacker who knows the 1-byte SS (or can enumerate all 256 possibilities) can trivially decrypt the ciphertext and recover the protected scalar `x`. This is a **Medium** impact finding: a public API reachable invariant break (no minimum KEM SS length) causes invalid cryptographic output with concrete security impact.

---

### Likelihood Explanation

The `cbmpc_pve_encrypt_with_kem` API is explicitly designed for third-party KEM integrations (HSM vendors, FFI wrappers). A malicious or non-conforming callback provider is a realistic attacker. The missing guard is a single missing length check, and the path is directly reachable from the public C API with no threshold or privilege requirement.

---

### Recommendation

Add a minimum KEM SS length check in `kem_encap_shim` (and symmetrically in `kem_decap_shim`) after the existing null/negative checks, mirroring the pattern already used in `kem_policy_rsa_oaep_hsm_t::decapsulate`:

```cpp
// After the existing kem_ss.size < 0 / null check:
constexpr int MIN_KEM_SS_BYTES = 16; // or 32 to match built-in policies
if (kem_ss.size < MIN_KEM_SS_BYTES) {
    if (kem_ct.data) cbmpc_cmem_free(kem_ct);
    cbmpc_free(kem_ss.data);
    return E_FORMAT;
}
```

Alternatively, enforce the check inside `kem_policy_runtime_kem_t::encapsulate` and `::decapsulate` in `pve_base.h` so the guard applies regardless of which shim is used.

---

### Proof of Concept

```c
// Malicious encap callback: always returns a 1-byte KEM SS
static cbmpc_error_t bad_encap(void* ctx,
                                cmem_t ek, cmem_t rho32,
                                cmem_t* out_kem_ct, cmem_t* out_kem_ss) {
    uint8_t* ct_buf = (uint8_t*)cbmpc_malloc(1);
    ct_buf[0] = 0xAB;
    out_kem_ct->data = ct_buf;
    out_kem_ct->size = 1;

    uint8_t* ss_buf = (uint8_t*)cbmpc_malloc(1);
    ss_buf[0] = 0x42;  // 1-byte "shared secret"
    out_kem_ss->data = ss_buf;
    out_kem_ss->size = 1;   // passes kem_ss.size < 0 and (size>0 && !data) checks
    return CBMPC_SUCCESS;
}

// In test:
cbmpc_pve_base_kem_t kem = { .ctx = NULL, .encap = bad_encap, .decap = NULL };
uint8_t fake_ek[4] = {0};
uint8_t label[5] = "test";
uint8_t x_bytes[32] = { /* some scalar */ };
cmem_t out_ct = {NULL, 0};

cbmpc_error_t rv = cbmpc_pve_encrypt_with_kem(
    &kem, CBMPC_CURVE_P256,
    (cmem_t){fake_ek, 4}, (cmem_t){label, 4},
    (cmem_t){x_bytes, 32}, &out_ct);

// Expected (with fix): rv != CBMPC_SUCCESS (E_FORMAT or E_CRYPTO)
// Actual (without fix): rv == CBMPC_SUCCESS, out_ct contains a ciphertext
//   whose AES-GCM key is derived from a 1-byte IKM (8 bits of security).
assert(rv != CBMPC_SUCCESS);  // FAILS without the fix
```

### Citations

**File:** src/cbmpc/c_api/pve_base_pke.cpp (L41-50)
```cpp
  if (kem_ss.size < 0 || (kem_ss.size > 0 && !kem_ss.data)) {
    cbmpc_free(kem_ss.data);
    if (kem_ct.data) cbmpc_cmem_free(kem_ct);
    return E_FORMAT;
  }
  out_kem_ct = coinbase::buf_t(kem_ct.data, kem_ct.size);
  out_kem_ss = coinbase::buf_t(kem_ss.data, kem_ss.size);
  cbmpc_cmem_free(kem_ct);
  cbmpc_cmem_free(kem_ss);
  return CBMPC_SUCCESS;
```

**File:** include-internal/cbmpc/internal/crypto/base_pki.h (L56-59)
```text
    // RFC 5869 HKDF: AES-GCM-256 key derivation from KEM shared secret
    buf_t prk = crypto::hkdf_extract_sha256(mem_t(), kem_ss);
    buf_t aes_key = crypto::hkdf_expand_sha256(prk, mem_t("CBMPC|KEM-AEAD|v1|KDF=HKDF-SHA256|AEAD=AES-GCM-256"), 32);
    crypto::aes_gcm_t::encrypt(aes_key, mem_t(iv, iv_size), aad, tag_size, plain, aead_ciphertext);
```

**File:** include-internal/cbmpc/internal/protocol/pve_base.h (L128-133)
```text
  static error_t encapsulate(const ek_t& pub_key, buf_t& kem_ct, buf_t& kem_ss, crypto::drbg_aes_ctr_t* drbg) {
    if (!pub_key.callbacks || !pub_key.callbacks->encap) return E_BADARG;
    constexpr int rho_size = 32;
    buf_t rho = drbg ? drbg->gen(rho_size) : crypto::gen_random(rho_size);
    return pub_key.callbacks->encap(pub_key.callbacks->ctx, pub_key.ek_bytes, rho, kem_ct, kem_ss);
  }
```

**File:** include-internal/cbmpc/internal/protocol/pve_base.h (L168-170)
```text
    // Our RSA-OAEP KEM policy uses a 32-byte shared secret (SHA-256 output size).
    const int expected_ss_size = crypto::hash_alg_t::get(crypto::hash_e::sha256).size;
    if (kem_ss.size() != expected_ss_size) return coinbase::error(E_CRYPTO, "invalid RSA KEM output size");
```
