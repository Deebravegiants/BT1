# Q3909: update_wallet_puzzle_hashes applies attacker-controlled batch semantics inconsistently

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `update_wallet_puzzle_hashes` and control batched spends, multi-coin updates, and partial-failure ordering so that `WalletStateManager.update_wallet_puzzle_hashes` in `chia/wallet/wallet_state_manager.py` executes a path where make `update_wallet_puzzle_hashes` apply a partially failing batch as if its individual spends still shared one security outcome, violating the invariant that batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/wallet_state_manager.py:595 `WalletStateManager.update_wallet_puzzle_hashes`
- Entrypoint: wallet RPC or wallet sync flow reaching `update_wallet_puzzle_hashes`
- Attacker controls: batched spends, multi-coin updates, and partial-failure ordering
- Exploit idea: make `update_wallet_puzzle_hashes` apply a partially failing batch as if its individual spends still shared one security outcome
- Invariant to test: batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: inject a mixed-success batch into `chia/wallet/wallet_state_manager.py:update_wallet_puzzle_hashes` and assert no partial failure rewrites unrelated valid spend outcomes
