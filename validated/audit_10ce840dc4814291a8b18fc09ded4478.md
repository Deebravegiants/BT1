### Title
Missing Key-Lockout Enforcement in `sign_with_global_abort()` Enables Iterative Private Key Recovery — (File: `src/cbmpc/protocol/ecdsa_2p.cpp`)

---

### Summary

`sign_with_global_abort()` and `sign_with_global_abort_batch()` in the internal API omit the ZK proof of correctness (`zk_ecdsa_sign_2pc_integer_commit_t`) that the standard `sign()` requires. When a malicious P2 sends a crafted Paillier ciphertext, P1 decrypts it, produces an invalid signature, detects the failure, and returns `E_ECDSA_2P_BIT_LEAK`. The library itself contains no mechanism to lock the key or prevent subsequent calls after this error. Each such triggered failure leaks one bit of P1's private key share `x1`. Repeated over ~256 sessions, a single malicious P2 recovers the full private key.

---

### Finding Description

`sign_batch_impl()` is the shared implementation for both signing modes, gated by `global_abort_mode`: [1](#0-0) 

In `SIGN_MODE_GLOBAL_ABORT`, P2 skips generating the ZK proof entirely: [2](#0-1) 

P1 skips verifying it: [3](#0-2) 

P1 then decrypts the unverified ciphertext `c[i]`, computes the signature, and checks it against the public key. If the check fails, it returns `E_ECDSA_2P_BIT_LEAK` and exits: [4](#0-3) 

The library then does nothing further. No key is locked, no counter is incremented, no state is mutated. The `key_t` struct passed in is `const`: [5](#0-4) 

The internal API header exposes both the single and batch variants: [6](#0-5) 

The public API (`include/cbmpc/api/ecdsa_2p.h`) does not expose these functions, but the internal API is a shipped, reachable entry point for integrators building on the library directly.

SECURE_USAGE.md explicitly acknowledges the gap: [7](#0-6) 

The library provides no enforcement mechanism — no key-state flag, no call counter, no automatic fallback to `sign()`. The entire burden is delegated to the caller with no API support.

---

### Impact Explanation

A malicious P2 can craft a Paillier ciphertext `c` such that after P1 decrypts it and reduces mod `q`, the resulting `s` value produces an invalid signature. The verification failure at line 395 is a 1-bit oracle on P1's private key share `x1`: P2 learns whether a specific linear combination of `x1` satisfies a chosen predicate. By repeating this across ~256 independent signing sessions (each with a fresh `sid`), P2 recovers all bits of `x1`. Combined with P2's own share `x2`, P2 reconstructs the full private key `x = x1 + x2 mod q`. This satisfies the Critical impact criterion: a single malicious peer recovers the private scalar without the required honest participation.

---

### Likelihood Explanation

Any integrator who uses the internal API to call `sign_with_global_abort()` for performance reasons (it saves one round and eliminates the expensive `zk_ecdsa_sign_2pc_integer_commit_t` proof) is exposed. The library provides no API-level guard, no key-state type that tracks whether a bit-leak has occurred, and no automatic downgrade to `sign()`. The documentation warns about this but provides no enforcement primitive. In a production wallet service where P2 is a user-controlled device, P2 is exactly the adversary this attack targets.

---

### Recommendation

1. Add a mutable `bit_leak_detected` flag to `key_t` (or a wrapper type) that is set atomically when `E_ECDSA_2P_BIT_LEAK` is returned.
2. At the entry of `sign_with_global_abort()`, check this flag and return an error immediately if set, preventing any further use of the key in global-abort mode.
3. Alternatively, remove `sign_with_global_abort()` from the internal API and require callers to opt in via an explicit, audited wrapper that enforces the lockout contract.
4. At minimum, add a runtime assertion or a stateful session object that tracks per-key abort counts and refuses further calls after the first detected bit-leak.

---

### Proof of Concept

**Setup**: P1 holds `x1`, P2 holds `x2`. Both call `sign_with_global_abort()` via the internal API.

**Attack loop** (P2 is malicious):

1. P2 participates honestly through rounds 1–3 (commitment, nonce exchange, decommitment).
2. In round 4, instead of computing the correct Paillier ciphertext `c = Enc(k2_inv*(m + x2*r) + rho*q)`, P2 sends a crafted `c'` that encodes a value designed to test a specific bit of `x1`.
3. P1 decrypts `c'`, computes `s' = Dec(c') / k1 mod q`, constructs the signature `(r, s')`, and calls `ecc_verification_key.verify(msg, sig)`.
4. Verification fails. P1 returns `E_ECDSA_2P_BIT_LEAK`.
5. Because the library does not lock `key`, P2 initiates a new session with the same key and repeats with a different crafted `c'` targeting the next bit.
6. After ~256 sessions, P2 has recovered all bits of `x1` and computes `x = x1 + x2 mod q`.

The critical code path is: [8](#0-7) [9](#0-8)

### Citations

**File:** src/cbmpc/protocol/ecdsa_2p.cpp (L241-245)
```cpp
error_t sign_batch_impl(job_2p_t& job, buf_t& sid, const key_t& key, const std::vector<mem_t>& msgs, int sign_mode_flag,
                        std::vector<buf_t>& sigs) {
  error_t rv = UNINITIALIZED_ERROR;

  bool global_abort_mode = sign_mode_flag == SIGN_MODE_GLOBAL_ABORT;
```

**File:** src/cbmpc/protocol/ecdsa_2p.cpp (L343-347)
```cpp
      if (!global_abort_mode) {
        if (rv = zk_ecdsa[i].prove(key.paillier, c_key_tag, pai_c, key.x_share * G, R2[i], m[i], r[i], k2[i],
                                   key.x_share, rho, rc, sid, i))
          return rv;
      }
```

**File:** src/cbmpc/protocol/ecdsa_2p.cpp (L351-354)
```cpp
  if (!global_abort_mode) {
    if (rv = job.p2_to_p1(c, zk_ecdsa)) return rv;
  } else {
    if (rv = job.p2_to_p1(c)) return rv;
```

**File:** src/cbmpc/protocol/ecdsa_2p.cpp (L364-374)
```cpp
      if (!global_abort_mode) {
        crypto::paillier_t::rerand_scope_t paillier_rerand(crypto::paillier_t::rerand_e::off);
        crypto::paillier_t::elem_t c_key_tag = key.paillier.elem(key.c_key) + (q << SEC_P_STAT);
        crypto::paillier_t::elem_t pai_c = key.paillier.elem(c[i]);

        ecc_point_t Q_pub_share = key.x_share * G;
        ecc_point_t Q_minus_xG;
        Q_minus_xG = key.Q - Q_pub_share;
        if (rv = zk_ecdsa[i].verify(curve, key.paillier, c_key_tag, pai_c, Q_minus_xG, R2[i], m[i], r[i], sid, i))
          return coinbase::error(rv, "zk_ecdsa_sign_2pc_integer_commit_t::verify failed");
      }
```

**File:** src/cbmpc/protocol/ecdsa_2p.cpp (L382-399)
```cpp
      bn_t s = key.paillier.decrypt(c[i]);
      s = q.mod(s);

      MODULO(q) { s /= k1[i]; }

      bn_t q_minus_s = q - s;
      if (q_minus_s < s) s = q_minus_s;

      crypto::ecdsa_signature_t sig(curve, r[i], s);
      sigs[i] = sig.to_der();

      // verify
      crypto::ecc_pub_key_t ecc_verification_key(key.Q);
      if (rv = ecc_verification_key.verify(msgs[i], sigs[i]))
        if (global_abort_mode)
          return coinbase::error(E_ECDSA_2P_BIT_LEAK, "signature verification failed");
        else
          return coinbase::error(rv, "signature verification failed");
```

**File:** include-internal/cbmpc/internal/protocol/ecdsa_2p.h (L53-55)
```text
error_t sign_with_global_abort(job_2p_t& job, buf_t& sid, const key_t& key, const mem_t msg, buf_t& sig);
error_t sign_with_global_abort_batch(job_2p_t& job, buf_t& sid, const key_t& key, const std::vector<mem_t>& msgs,
                                     std::vector<buf_t>& sigs);
```

**File:** SECURE_USAGE.md (L187-188)
```markdown
We intentionally do not expose a more efficient "global-abort" variant of two-party signing in the public API, because using it safely requires additional cryptographic and operational expertise as described below. The `sign_with_global_abort()` is secure as long as if a certain type of cheating is detected, all executions with that key are halted. This is because such a cheat can be used to learn a bit of the private key. This is insignificant for a small number of bits (as they can be guessed anyway) but can leak the entire private key over time if the attack is allowed to be carried out multiple times over many signing attempts. This also means that it isn't secure to open hundreds of signing sessions in parallel, if it isn't possible to abort them all in case cheating is detected in an ... (truncated)
We stress that this is the only protocol in the library with this property. We also stress that the *application* using the library is responsible for ensuring that appropriate action is taken (locking the key, moving to `sign()`, etc.) if the `E_ECDSA_2P_BIT_LEAK` error is received. *This is **not** taken care of by the low-level library*.
```
