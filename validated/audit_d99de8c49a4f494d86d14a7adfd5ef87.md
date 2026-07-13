Looking at the code carefully to trace the exact exploit path.

### Title
Insufficient Small-Factor Bound in `check_integer_with_small_primes` Allows ZK-Valid-Paillier Soundness Bypass - (`include-internal/cbmpc/internal/zk/small_primes.h`, `src/cbmpc/zk/zk_paillier.cpp`)

### Summary

`valid_paillier_t::verify` calls `check_integer_with_small_primes(N, param::alpha)` where `param::alpha = 8192`. The check only rejects N if it has a prime factor ≤ 8192. The `small_primes` array contains 10,000 primes up to 104,729, but the loop breaks at the first prime exceeding `alpha`. The first prime above 8192 is 8209, which is present in the array but is never tested. An attacker can construct N = 8209 * q (q a large prime) — passing the small-factor check — while knowing phi(N) = 8208*(q-1), and use that knowledge to forge valid sigma values, causing `paillier_valid_key` to be set to `zk_flag::verified` for a modulus whose factorization is fully known to the attacker.

### Finding Description

**Parameter mismatch between the check bound and the array coverage:**

`param_t::alpha` is defined as `1 << log_alpha = 1 << 13 = 8192`. [1](#0-0) 

`check_integer_with_small_primes` iterates the `small_primes` array and breaks as soon as `small_prime > alpha`: [2](#0-1) 

The array ends at 104,729 (10,000 entries), but with `alpha = 8192` the loop exits after testing 8191 and never tests 8209 or any larger prime: [3](#0-2) [4](#0-3) 

**The ZK proof check that is bypassed:**

`valid_paillier_t::verify` first calls the small-factor check, then verifies `sigma[i]^N ≡ rho[i] (mod N)` for deterministic `rho[i]` derived from `hash(N, session_id, aux)`: [5](#0-4) 

The rho values are fully public (derived from public inputs), so an attacker who knows phi(N) can compute `N_inv = N^{-1} mod phi(N)` and set `sigma[i] = rho[i]^{N_inv} mod N`. This satisfies `sigma[i]^N ≡ rho[i] (mod N)` exactly as a legitimate prover would. [6](#0-5) 

**No minimum bit-size guard in `valid_paillier_t::verify`:**

`paillier_t::create_pub` only rejects N larger than 2048 bits, not smaller: [7](#0-6) 

`valid_paillier_t::verify` itself has no bit-size check, so N = 8209 * q (q a ~2040-bit prime, making N ≈ 2048 bits) is accepted at every layer.

**The same flawed bound is used in all dependent ZK proofs:**

`valid_paillier_interactive_t::verify`, `paillier_zero_t::verify`, `two_paillier_equal_t::verify`, `two_paillier_equal_interactive_t::verify`, and `pdl_t::verify` all call `check_integer_with_small_primes(N, valid_paillier_t::param::alpha)` with the same `alpha = 8192`: [8](#0-7) [9](#0-8) [10](#0-9) 

### Impact Explanation

A Byzantine peer (e.g., P1 in the 2P ECDSA DKG) generates N = 8209 * q, passes `valid_paillier_t::verify`, and has `paillier_valid_key = zk_flag::verified` accepted by the honest party. The honest party then uses this key for Paillier encryption of secret material (key shares, nonce shares) in subsequent protocol steps. Because the attacker knows phi(N), they can decrypt all ciphertexts produced under N, recovering the honest party's secret shares and compromising the entire DKG/signing session.

The DKG entry point where P2 verifies P1's Paillier key and then uses it: [11](#0-10) 

### Likelihood Explanation

The attack requires only:
1. Choosing p = 8209 (or any prime in [8193, 104729]) and a large prime q.
2. Computing phi(N) = (p-1)(q-1) — trivial given p.
3. Computing N^{-1} mod phi(N) — standard modular inverse.
4. Computing rho[i] from the public DRBG — same computation the verifier performs.
5. Computing sigma[i] = rho[i]^{N_inv} mod N — one modular exponentiation per round.

The coprime check `!mod_t::coprime(rho_prod, N)` passes with probability ≥ (1 - 1/8209)^t ≈ 0.9988 for t = 10 rounds, so no retries are needed in practice.

### Recommendation

Change `param_t::log_alpha` so that `alpha` covers all primes in the `small_primes` array. The array ends at 104,729, so `alpha` must be at least 104,729. Alternatively, remove the `alpha` early-exit entirely and always scan all 10,000 entries. The same fix must be applied consistently everywhere `check_integer_with_small_primes` is called with `valid_paillier_t::param::alpha`.

### Proof of Concept

```
// Attacker constructs N = p * q, p = 8209, q = large prime (~2040 bits)
bn_t p = 8209;
bn_t q = bn_t::generate_prime(2040, false);
bn_t N = p * q;
bn_t phi_N = (p - 1) * (q - 1);   // = 8208 * (q-1), known to attacker

// Compute N^{-1} mod phi(N)
bn_t N_inv = BN_mod_inverse(N, phi_N);

// Replicate the verifier's DRBG to get rho values
buf128_t k = crypto::ro::hash_string(N, session_id, aux).bitlen128();
crypto::drbg_aes_ctr_t drbg(k);

for (int i = 0; i < param::t; i++) {
    bn_t rho = drbg.gen_bn(N);
    sigma[i] = rho.pow_mod(N_inv, N);  // sigma[i]^N ≡ rho[i] (mod N) ✓
}

// valid_paillier_t::verify:
//   check_integer_with_small_primes(N, 8192) → SUCCESS (8209 > 8192, not checked)
//   sigma[i]^N mod N == rho[i]              → SUCCESS (by construction)
//   coprime(rho_prod, N)                    → SUCCESS (overwhelming probability)
//   paillier_valid_key = zk_flag::verified  ← attacker wins
```

### Citations

**File:** include-internal/cbmpc/internal/zk/zk_util.h (L28-30)
```text
  inline static constexpr int log_alpha = 13;
  inline static constexpr int padded_log_alpha = 16;  // rounded up multiple of 8 for byte alignment
  inline static constexpr int alpha = 1 << log_alpha;
```

**File:** include-internal/cbmpc/internal/zk/small_primes.h (L11-18)
```text
static error_t check_integer_with_small_primes(const bn_t& prime, int alpha) {
  for (int i = 0; i < small_primes_count; i++) {
    int small_prime = small_primes[i];
    if (small_prime > alpha) break;
    if (mod_t::mod(prime, small_prime) == 0) return coinbase::error(E_CRYPTO);
  }
  return SUCCESS;
}
```

**File:** src/cbmpc/zk/small_primes.cpp (L80-80)
```cpp
    8147,   8161,   8167,   8171,   8179,   8191,   8209,   8219,   8221,   8231,   8233,   8237,   8243,   8263,
```

**File:** src/cbmpc/zk/small_primes.cpp (L721-722)
```cpp
    104711, 104717, 104723, 104729,
};
```

**File:** src/cbmpc/zk/zk_paillier.cpp (L7-22)
```cpp
void valid_paillier_t::prove(const crypto::paillier_t& paillier, mem_t session_id, uint64_t aux) {
  cb_assert(paillier.has_private_key());
  const mod_t& N = paillier.get_N();
  const bn_t& phi_N = paillier.get_phi_N();

  bn_t N_inv = mod_t::N_inv_mod_phiN_2048(N, phi_N);

  static_assert(SEC_P_COM == 128, "security parameter changed, please update the code");
  buf128_t k = crypto::ro::hash_string(N, session_id, aux).bitlen128();
  crypto::drbg_aes_ctr_t drbg(k);

  for (int i = 0; i < param::t; i++) {
    bn_t rho = drbg.gen_bn(N);
    sigma[i] = rho.pow_mod(N_inv, N);
  }
}
```

**File:** src/cbmpc/zk/zk_paillier.cpp (L33-47)
```cpp
  if (paillier_no_small_factors == zk_flag::unverified) {
    if (rv = check_integer_with_small_primes(N, param::alpha)) return rv;
    paillier_no_small_factors = zk_flag::verified;
  }

  bn_t rho_prod = 1;
  for (int i = 0; i < param::t; i++) {
    bn_t rho = drbg.gen_bn(N);
    MODULO(N) rho_prod *= rho;
    if (sigma[i] <= 0) return coinbase::error(E_CRYPTO);
    if (sigma[i].pow_mod(N, N) != rho) return coinbase::error(E_CRYPTO);
  }
  if (!mod_t::coprime(rho_prod, N)) return coinbase::error(E_CRYPTO);
  paillier_valid_key = zk_flag::verified;
  return SUCCESS;
```

**File:** src/cbmpc/zk/zk_paillier.cpp (L86-88)
```cpp
  if (paillier_no_small_factors == zk_flag::unverified) {
    if (rv = check_integer_with_small_primes(N, param::alpha)) return rv;
    paillier_no_small_factors = zk_flag::verified;
```

**File:** src/cbmpc/zk/zk_paillier.cpp (L146-148)
```cpp
  if (paillier_no_small_factors == zk_flag::unverified) {
    if (rv = check_integer_with_small_primes(N, valid_paillier_t::param::alpha)) return rv;
    paillier_no_small_factors = zk_flag::verified;
```

**File:** src/cbmpc/zk/zk_paillier.cpp (L253-259)
```cpp
  if (p0_no_small_factors == zk_flag::unverified) {
    if (rv = check_integer_with_small_primes(N0, valid_paillier_t::param::alpha)) return rv;
    p0_no_small_factors = zk_flag::verified;
  }
  if (p1_no_small_factors == zk_flag::unverified) {
    if (rv = check_integer_with_small_primes(N1, valid_paillier_t::param::alpha)) return rv;
    p1_no_small_factors = zk_flag::verified;
```

**File:** src/cbmpc/crypto/base_paillier.cpp (L148-155)
```cpp
error_t paillier_t::create_pub(const bn_t& theN) {
  if (!mod_t::is_valid_modulus(theN)) return E_BADARG;
  if (theN.get_bits_count() > bit_size) return E_BADARG;
  N = mod_t(theN, /* multiplicative_dense */ true);
  has_private = false;
  update_public();
  return SUCCESS;
}
```

**File:** src/cbmpc/protocol/ecdsa_2p.cpp (L85-125)
```cpp
error_t dkg(job_2p_t& job, ecurve_t curve, key_t& key) {
  error_t rv = UNINITIALIZED_ERROR;

  key.curve = curve;
  const mod_t& q = curve.order();

  paillier_gen_interactive_t paillier_gen(job.get_pid(party_t::p1));
  eckey::dkg_2p_t ec_dkg(curve, job.get_pid(party_t::p1));

  key.x_share = bn_t::rand(q);
  key.role = job.get_party();

  if (job.is_p1()) {
    ec_dkg.step1_p1_to_p2(key.x_share);
    paillier_gen.step1_p1_to_p2(key.paillier, key.x_share, ec_dkg.curve.order(), key.c_key);
  }

  if (rv = job.p1_to_p2(ec_dkg.msg1, paillier_gen.msg1, key.c_key)) return rv;
  if (paillier_gen.c_key != key.c_key) return coinbase::error(E_CRYPTO, "paillier_gen.c_key != key.c_key");

  if (job.is_p2()) {
    ec_dkg.step2_p2_to_p1(key.x_share);
    paillier_gen.step2_p2_to_p1();
  }

  if (rv = job.p2_to_p1(ec_dkg.msg2, paillier_gen.msg2)) return rv;

  if (job.is_p1()) {
    if (rv = ec_dkg.step3_p1_to_p2(key.Q)) return rv;
    paillier_gen.step3_p1_to_p2(key.paillier, key.x_share, ec_dkg.Q1, job.get_pid(party_t::p1), ec_dkg.sid);
  }

  if (rv = job.p1_to_p2(ec_dkg.msg3, paillier_gen.msg3)) return rv;

  if (job.is_p2()) {
    if (rv = ec_dkg.step4_output_p2(key.Q)) return rv;
    if (rv = paillier_gen.step4_p2_output(key.paillier, ec_dkg.Q1, paillier_gen.c_key, job.get_pid(party_t::p1),
                                          ec_dkg.sid))
      return rv;
  }
  return SUCCESS;
```
