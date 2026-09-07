# [?] fix: prevent integer overflow in GetLastStateProof size guard

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2026-06-02
Source: https://github.com/nervosnetwork/ckb/commit/422889c7d4bf20d4c538da7a1fe0bbc15a227f13
Type: security-commit

## Details
fix: prevent integer overflow in GetLastStateProof size guard

The guard computes difficulties.len() + (last_n_blocks as usize) * 2
to compare against GET_LAST_STATE_PROOF_LIMIT.  With attacker-controlled
last_n_blocks, the multiplication can overflow:

- Under overflow-checks (debug) → panic → process termination
- Under wrapping (release) → bypasses the limit check, allowing a huge
  last_n_blocks to flow into downstream logic which collects block ranges
  into unbounded Vecs → resource exhaustion

Use saturating_add and saturating_mul so that any overflow saturates at
usize::MAX, which is always > GET_LAST_STATE_PROOF_LIMIT (1000),
correctly firing the guard in all cases.
