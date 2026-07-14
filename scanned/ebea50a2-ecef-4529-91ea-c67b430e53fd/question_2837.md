# Q2837: generate_issuance_bundle applies attacker-controlled batch semantics inconsistently

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `generate_issuance_bundle` and control batched spends, multi-coin updates, and partial-failure ordering so that `GenesisById.generate_issuance_bundle` in `chia/wallet/puzzles/tails.py` executes a path where make `generate_issuance_bundle` apply a partially failing batch as if its individual spends still shared one security outcome, violating the invariant that batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/puzzles/tails.py:92 `GenesisById.generate_issuance_bundle`
- Entrypoint: wallet RPC or wallet sync flow reaching `generate_issuance_bundle`
- Attacker controls: batched spends, multi-coin updates, and partial-failure ordering
- Exploit idea: make `generate_issuance_bundle` apply a partially failing batch as if its individual spends still shared one security outcome
- Invariant to test: batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: inject a mixed-success batch into `chia/wallet/puzzles/tails.py:generate_issuance_bundle` and assert no partial failure rewrites unrelated valid spend outcomes
