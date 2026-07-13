Looking at the key components:

**`check_integer_with_small_primes` logic** (`include-internal/cbmpc/internal/zk/small_primes.h`, lines 11-18):
```cpp
static error_t check_integer_with_small_primes(const bn_t& prime, int alpha) {
  for (int i = 0; i < small_primes_count; i++) {
    int small_prime = small_primes[i];
    if (small_prime > alpha) break;   // stops at alpha
    if (mod_t::mod(prime, small_prime) == 0) return coinbase::error(E_CRYPTO);
  }
  return SUCCESS;
}
```

**`param_t::alpha`** (`include-internal/cbmpc/internal/zk/zk_util.h`, line 30): `alpha = 1 << 13 = 8192`

**`small_primes[]` last entry** (`src/cbmpc/zk/small_primes.cpp`, line 721): `104729`

**`valid_paillier_t::verify` call** (`src/cbmpc/zk/zk_paillier.cpp`, line 34): `check_integer_with_small_primes(N, param::alpha)` — i.e., alpha=8192

The same alpha=8192 is used in every `check_integer_with_small_primes` call across `pdl_t::verify`, `paillier_zero_t::verify`, `two_paillier_equal_t::verify`, and `paillier_pedersen_equal_t::verify`.

---

### Title
Small-Prime Boundary Mismatch in `check_integer_with_small_primes` Allows Weak Paillier Modulus Acceptance — (`include-internal/cbmpc/internal/zk/small_primes.h`, `src/cbmpc/zk/zk_paillier.cpp`)

### Summary
The `check_integer_with_small_primes` function iterates the `small_primes[]` array (which contains 10,000 primes up to 104,729) but breaks as soon as `small_prime > alpha`, where `alpha = 8192` is the hardcoded value from `param_t`. Primes in the array between 8,193 and 104,729 are never tested. A malicious prover can construct a Paillier modulus N = p × q where p is a prime in that gap (e.g., p = 8,209, the first prime > 8,192 in the array) and pass every `check_integer_with_small_primes` call in the codebase, causing `valid_paillier_t::verify` (and all downstream verifiers) to accept a structurally weak N.

### Finding Description

`param_t::alpha` is defined as `1 << log_alpha = 1 << 13 = 8192`. [1](#0-0) 

`check_integer_with_small_primes` breaks out of the loop the moment `small_prime > alpha`: [2](#0-1) 

The `small_primes[]` array's last entry is 104,729: [3](#0-2) 

`valid_paillier_t::verify` calls `check_integer_with_small_primes(N, param::alpha)` — alpha=8192 — and on success sets `paillier_no_small_factors = zk_flag::verified`: [4](#0-3) 

The same alpha=8192 cutoff is used in every downstream verifier:
- `pdl_t::verify` [5](#0-4) 
- `paillier_zero_t::verify` [6](#0-5) 
- `two_paillier_equal_t::verify` [7](#0-6) 
- `paillier_pedersen_equal_t::verify` [8](#0-7) 

A malicious prover constructs N = 8209 × q (q a large prime). They know φ(N) = 8208 × (q−1), compute N_inv = N⁻¹ mod φ(N), and produce valid `sigma[i]` values. The verifier's loop breaks at index where `small_prime = 8209 > 8192`, never testing divisibility by 8209. Both `paillier_no_small_factors` and `paillier_valid_key` are set to `verified`. All downstream ZK verifiers inherit these flags and skip their own small-prime checks.

### Impact Explanation

The security of every Paillier-based ZK proof in this codebase (`pdl_t`, `paillier_zero_t`, `two_paillier_equal_t`, `paillier_pedersen_equal_t`) depends on N having no small prime factors. With N = 8209 × q:

1. N is trivially factorable by trial division — any party (or external observer) can recover φ(N).
2. The Paillier scheme loses semantic security: all ciphertexts under N are decryptable by anyone who factors N.
3. In the ECDSA 2P protocol (`ecdsa_2p.cpp`), P2 propagates the `paillier_valid_key` and `paillier_no_small_factors` flags from `valid_paillier_t` directly into `pdl_t` and `two_paillier_equal_t` without re-checking: [9](#0-8) 
4. The accepted weak N means the soundness assumptions of the downstream ZK proofs are violated, producing accepted-but-invalid cryptographic output.

### Likelihood Explanation

The attack requires only that the malicious party generate N = p × q with p in (8192, 104729] and produce a valid `valid_paillier_t` proof — both are straightforward given knowledge of φ(N). No threshold collusion or privileged access is needed. The malicious party is a standard protocol peer (P1 in the 2P ECDSA flow).

### Recommendation

Change `alpha` to match the actual maximum prime in the `small_primes[]` array (104,729), or alternatively trim the array to only contain primes ≤ 8,192. The simplest fix is to replace the hardcoded `param_t::alpha = 1 << 13` cutoff passed to `check_integer_with_small_primes` with `small_primes[small_primes_count - 1]` (the array's actual maximum), ensuring the full array is always scanned. Alternatively, add a `static_assert` that `small_primes[small_primes_count - 1] <= alpha` to catch future mismatches at compile time.

### Proof of Concept

```cpp
// Deterministic unit test demonstrating the boundary mismatch
TEST(SmallPrimes, BoundaryMismatch_8209_AcceptedByAlpha8192_RejectedByFullArray) {
  coinbase::crypto::vartime_scope_t vartime_scope;

  // p = 8209 is the first prime > 8192 in small_primes[]
  // N = 8209 * large_prime is trivially factorable
  bn_t p = bn_t(8209);
  bn_t q_large = bn_t::generate_prime(1024, false, nullptr, nullptr);
  bn_t N = p * q_large;

  // With alpha=8192 (current production value): PASSES — 8209 is never tested
  EXPECT_EQ(coinbase::zk::check_integer_with_small_primes(N, 8192), SUCCESS);

  // With alpha=104729 (array's actual maximum): REJECTS — 8209 is caught
  EXPECT_NE(coinbase::zk::check_integer_with_small_primes(N, 104729), SUCCESS);

  // Demonstrates: valid_paillier_t::verify would accept this weak N
  // because it calls check_integer_with_small_primes(N, param::alpha) with alpha=8192
}
```

### Citations

**File:** include-internal/cbmpc/internal/zk/zk_util.h (L28-31)
```text
  inline static constexpr int log_alpha = 13;
  inline static constexpr int padded_log_alpha = 16;  // rounded up multiple of 8 for byte alignment
  inline static constexpr int alpha = 1 << log_alpha;
  inline static constexpr int alpha_bits_mask = alpha - 1;
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

**File:** src/cbmpc/zk/small_primes.cpp (L721-722)
```cpp
    104711, 104717, 104723, 104729,
};
```

**File:** src/cbmpc/zk/zk_paillier.cpp (L33-36)
```cpp
  if (paillier_no_small_factors == zk_flag::unverified) {
    if (rv = check_integer_with_small_primes(N, param::alpha)) return rv;
    paillier_no_small_factors = zk_flag::verified;
  }
```

**File:** src/cbmpc/zk/zk_paillier.cpp (L146-149)
```cpp
  if (paillier_no_small_factors == zk_flag::unverified) {
    if (rv = check_integer_with_small_primes(N, valid_paillier_t::param::alpha)) return rv;
    paillier_no_small_factors = zk_flag::verified;
  }
```

**File:** src/cbmpc/zk/zk_paillier.cpp (L253-260)
```cpp
  if (p0_no_small_factors == zk_flag::unverified) {
    if (rv = check_integer_with_small_primes(N0, valid_paillier_t::param::alpha)) return rv;
    p0_no_small_factors = zk_flag::verified;
  }
  if (p1_no_small_factors == zk_flag::unverified) {
    if (rv = check_integer_with_small_primes(N1, valid_paillier_t::param::alpha)) return rv;
    p1_no_small_factors = zk_flag::verified;
  }
```

**File:** src/cbmpc/zk/zk_paillier.cpp (L497-500)
```cpp
  if (paillier_no_small_factors == zk_flag::unverified) {
    if (rv = check_integer_with_small_primes(N, valid_paillier_t::param::alpha)) return rv;
    paillier_no_small_factors = zk_flag::verified;
  }
```

**File:** src/cbmpc/zk/zk_pedersen.cpp (L338-341)
```cpp
  if (paillier_no_small_factors == zk_flag::unverified) {
    if (rv = check_integer_with_small_primes(N, param::alpha)) return rv;
    paillier_no_small_factors = zk_flag::verified;
  }
```

**File:** src/cbmpc/protocol/ecdsa_2p.cpp (L73-80)
```cpp
  pdl.paillier_valid_key = valid.paillier_valid_key;
  pdl.paillier_no_small_factors = valid.paillier_no_small_factors;
  pdl.paillier_range_exp_slack_proof = zk::zk_flag::skip;
  if (rv = pdl.verify(c_key, paillier, Q1, sid, 0)) return rv;

  equal.paillier_valid_key = valid.paillier_valid_key;
  equal.paillier_no_small_factors = valid.paillier_no_small_factors;
  if (rv = equal.verify(paillier, c_key, q, Com)) return rv;
```
