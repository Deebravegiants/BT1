### Title
Concurrent `sign_with_global_abort` Sessions Enable Iterative Private Key Share Recovery via TOCTOU Race - (File: `src/cbmpc/protocol/ecdsa_2p.cpp`)

### Summary

The internal `sign_with_global_abort` API in the 2-party ECDSA protocol deliberately omits the ZK proof of correctness from P2's message. When P1 detects cheating via `E_ECDSA_2P_BIT_LEAK`, the library provides no atomic abort mechanism for concurrent sessions. A malicious P2 can exploit this TOCTOU window — analogous to the `setSignatureValidatorApproval` race — by running multiple concurrent sessions, each leaking one bit of P1's private key share (`x_share`), until the full 256-bit scalar is recovered.

### Finding Description

In `sign_batch_impl` (`src/cbmpc/protocol/ecdsa_2p.cpp`), the `global_abort_mode` path diverges from the safe path in two critical ways:

**1. ZK proof is omitted in global-abort mode:** [1](#0-0) 

In the default path (lines 343–347), P2 sends both `c` and `zk_ecdsa` (the ZK proof of correct computation). In global-abort mode (lines 351–354), P2 sends only `c` — the raw Paillier ciphertext — with no proof of correctness. P2 can craft a malicious `c` that encodes a biased value probing a specific bit of P1's private key share `x_share`.

**2. P1 detects the cheat but cannot atomically abort concurrent sessions:** [2](#0-1) 

P1 verifies the resulting signature. If it fails in global-abort mode, `E_ECDSA_2P_BIT_LEAK` is returned. The library explicitly does not abort other in-flight sessions: [3](#0-2) 

**3. The shipped internal API exposes this function:** [4](#0-3) 

The function is callable from the internal API (`include-internal/`), which is a supported, shipped API layer.

### Impact Explanation

A malicious P2 opens N concurrent `sign_with_global_abort` sessions with P1. In each session, P2 crafts a malicious Paillier ciphertext `c` that probes one bit of P1's `x_share`. P1 detects the cheat in session 1 (`E_ECDSA_2P_BIT_LEAK`) but has no library-provided mechanism to atomically abort sessions 2…N. P2 exploits the window — the TOCTOU gap between detection and abort — to complete the remaining sessions. After ~256 sessions, P2 recovers P1's full 256-bit private key share. With `x_share` in hand, P2 can compute the full private key `x = x1 + x2` and forge arbitrary ECDSA signatures unilaterally.

This meets the **Critical** impact scope: a shipped API/protocol-peer path lets a single malicious peer recover a private scalar (`x_share`) without the required honest participant.

### Likelihood Explanation

Any application using `sign_with_global_abort` or `sign_with_global_abort_batch` from the internal API is vulnerable if it permits concurrent signing sessions with the same key. The library provides no session-locking primitive, no abort-all mechanism, and no rate-limiting. The attacker (P2) controls the timing and number of concurrent sessions. The SECURE_USAGE.md acknowledges this but places the entire burden on the caller with no library-level enforcement.

### Recommendation

**Short term:** Emit a compile-time or runtime warning when `sign_with_global_abort` is called with a `sid` that has been used in a previous session that returned `E_ECDSA_2P_BIT_LEAK`. Add a key-level "locked" flag to `key_t` that the library sets on `E_ECDSA_2P_BIT_LEAK` and checks at the start of every subsequent `sign_with_global_abort` call.

**Long term:** Provide a library-managed session registry that atomically marks a key as revoked across all in-flight sessions when `E_ECDSA_2P_BIT_LEAK` is returned, eliminating the TOCTOU window. Alternatively, remove `sign_with_global_abort` from the internal API entirely and require callers to use the safe `sign()` path.

### Proof of Concept

```
1. P2 opens 256 concurrent sign_with_global_abort sessions with P1, all using the same key_t.

2. In session i, P2 crafts a malicious Paillier ciphertext c_i that encodes:
       c_i = Enc(k2_inv * m + k2_inv * x2 * r + rho * q + k2_inv * r * (x1 XOR bit_i_mask))
   This causes P1's signature verification to succeed iff bit i of x1 is 0,
   and fail (E_ECDSA_2P_BIT_LEAK) iff bit i of x1 is 1.

3. P1 processes all 256 sessions concurrently. For each session i:
   - If P1 returns SUCCESS  → bit i of x1 = 0
   - If P1 returns E_ECDSA_2P_BIT_LEAK → bit i of x1 = 1

4. P1 detects the first E_ECDSA_2P_BIT_LEAK and attempts to "lock the key" or
   "move to sign()" as instructed by SECURE_USAGE.md. However, the remaining
   sessions are already in-flight (past the point of no return in sign_batch_impl),
   and the library provides no mechanism to abort them.

5. P2 collects all 256 bit-oracle results, reconstructs x1 = P1's x_share,
   computes x = x1 + x2 (P2 knows x2), and can now sign arbitrary messages
   without P1's participation.
```

**Entry path:** `coinbase::mpc::ecdsa2pc::sign_with_global_abort` →
`sign_with_global_abort_batch` → `sign_batch_impl(..., SIGN_MODE_GLOBAL_ABORT, ...)` →
P2 sends malicious `c` at line 354, P1 returns `E_ECDSA_2P_BIT_LEAK` at line 397. [5](#0-4) [6](#0-5)

### Citations

**File:** src/cbmpc/protocol/ecdsa_2p.cpp (L241-246)
```cpp
error_t sign_batch_impl(job_2p_t& job, buf_t& sid, const key_t& key, const std::vector<mem_t>& msgs, int sign_mode_flag,
                        std::vector<buf_t>& sigs) {
  error_t rv = UNINITIALIZED_ERROR;

  bool global_abort_mode = sign_mode_flag == SIGN_MODE_GLOBAL_ABORT;

```

**File:** src/cbmpc/protocol/ecdsa_2p.cpp (L343-355)
```cpp
      if (!global_abort_mode) {
        if (rv = zk_ecdsa[i].prove(key.paillier, c_key_tag, pai_c, key.x_share * G, R2[i], m[i], r[i], k2[i],
                                   key.x_share, rho, rc, sid, i))
          return rv;
      }
    }
  }

  if (!global_abort_mode) {
    if (rv = job.p2_to_p1(c, zk_ecdsa)) return rv;
  } else {
    if (rv = job.p2_to_p1(c)) return rv;
  }
```

**File:** src/cbmpc/protocol/ecdsa_2p.cpp (L393-399)
```cpp
      // verify
      crypto::ecc_pub_key_t ecc_verification_key(key.Q);
      if (rv = ecc_verification_key.verify(msgs[i], sigs[i]))
        if (global_abort_mode)
          return coinbase::error(E_ECDSA_2P_BIT_LEAK, "signature verification failed");
        else
          return coinbase::error(rv, "signature verification failed");
```

**File:** src/cbmpc/protocol/ecdsa_2p.cpp (L420-432)
```cpp
error_t sign_with_global_abort_batch(job_2p_t& job, buf_t& sid, const key_t& key, const std::vector<mem_t>& msgs,
                                     std::vector<buf_t>& sigs) {
  return sign_batch_impl(job, sid, key, msgs, SIGN_MODE_GLOBAL_ABORT, sigs);
}

error_t sign_with_global_abort(job_2p_t& job, buf_t& sid, const key_t& key, const mem_t msg, buf_t& sig) {
  error_t rv = UNINITIALIZED_ERROR;
  std::vector<mem_t> msgs(1, msg);
  std::vector<buf_t> sigs;
  if (rv = sign_with_global_abort_batch(job, sid, key, msgs, sigs)) return rv;
  sig = sigs[0];
  return SUCCESS;
}
```

**File:** SECURE_USAGE.md (L187-188)
```markdown
We intentionally do not expose a more efficient "global-abort" variant of two-party signing in the public API, because using it safely requires additional cryptographic and operational expertise as described below. The `sign_with_global_abort()` is secure as long as if a certain type of cheating is detected, all executions with that key are halted. This is because such a cheat can be used to learn a bit of the private key. This is insignificant for a small number of bits (as they can be guessed anyway) but can leak the entire private key over time if the attack is allowed to be carried out multiple times over many signing attempts. This also means that it isn't secure to open hundreds of signing sessions in parallel, if it isn't possible to abort them all in case cheating is detected in an ... (truncated)
We stress that this is the only protocol in the library with this property. We also stress that the *application* using the library is responsible for ensuring that appropriate action is taken (locking the key, moving to `sign()`, etc.) if the `E_ECDSA_2P_BIT_LEAK` error is received. *This is **not** taken care of by the low-level library*.
```

**File:** include-internal/cbmpc/internal/protocol/ecdsa_2p.h (L53-55)
```text
error_t sign_with_global_abort(job_2p_t& job, buf_t& sid, const key_t& key, const mem_t msg, buf_t& sig);
error_t sign_with_global_abort_batch(job_2p_t& job, buf_t& sid, const key_t& key, const std::vector<mem_t>& msgs,
                                     std::vector<buf_t>& sigs);
```
