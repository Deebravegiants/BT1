# Q1774: create_absorb_spend applies attacker-controlled batch semantics inconsistently

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `create_absorb_spend` and control batched spends, multi-coin updates, and partial-failure ordering so that `create_absorb_spend` in `chia/pools/pool_puzzles.py` executes a path where make `create_absorb_spend` apply a partially failing batch as if its individual spends still shared one security outcome, violating the invariant that batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/pools/pool_puzzles.py:252 `create_absorb_spend`
- Entrypoint: pool wallet or singleton spend flow reaching `create_absorb_spend`
- Attacker controls: batched spends, multi-coin updates, and partial-failure ordering
- Exploit idea: make `create_absorb_spend` apply a partially failing batch as if its individual spends still shared one security outcome
- Invariant to test: batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: inject a mixed-success batch into `chia/pools/pool_puzzles.py:create_absorb_spend` and assert no partial failure rewrites unrelated valid spend outcomes
