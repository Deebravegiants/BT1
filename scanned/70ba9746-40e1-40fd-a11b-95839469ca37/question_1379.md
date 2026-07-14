# Q1379: new_tx_block accepts a spend path that diverges between validation stages

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `new_tx_block` and control conflicting spend bundle fields, CLVM conditions, announcements, and fee/cost edge cases so that `Mempool.new_tx_block` in `chia/full_node/mempool.py` executes a path where drive `new_tx_block` through two validation paths that should be equivalent, but make one path accept a spend bundle the other path rejects, violating the invariant that mempool admission, block validation, and wallet accounting must agree on whether the same spend is valid and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/mempool.py:329 `Mempool.new_tx_block`
- Entrypoint: full node mempool, sync, or peer flow reaching `new_tx_block`
- Attacker controls: conflicting spend bundle fields, CLVM conditions, announcements, and fee/cost edge cases
- Exploit idea: drive `new_tx_block` through two validation paths that should be equivalent, but make one path accept a spend bundle the other path rejects
- Invariant to test: mempool admission, block validation, and wallet accounting must agree on whether the same spend is valid
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: unit-test `chia/full_node/mempool.py:new_tx_block` with paired spend bundles that differ only in one edge-condition and assert mempool acceptance equals block acceptance
