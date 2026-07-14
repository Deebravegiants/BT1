# Q97: validated_signature mixes fork state across rollback or peak changes

## Question
Can an unprivileged attacker reach peer-supplied block, proof, or spend path reaching `validated_signature` and control peak announcements, fork shapes, rollback order, and block delivery timing so that `PreValidationResult.validated_signature` in `chia/consensus/multiprocess_validation.py` executes a path where interleave peak changes and rollback-sensitive inputs so `validated_signature` mixes fork-specific state across chains, violating the invariant that fork-local state must not leak across rollback and reorg boundaries and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/consensus/multiprocess_validation.py:54 `PreValidationResult.validated_signature`
- Entrypoint: peer-supplied block, proof, or spend path reaching `validated_signature`
- Attacker controls: peak announcements, fork shapes, rollback order, and block delivery timing
- Exploit idea: interleave peak changes and rollback-sensitive inputs so `validated_signature` mixes fork-specific state across chains
- Invariant to test: fork-local state must not leak across rollback and reorg boundaries
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: script a reorg harness around `chia/consensus/multiprocess_validation.py:validated_signature` with interleaved peaks and assert fork-local state never leaks across rollback
