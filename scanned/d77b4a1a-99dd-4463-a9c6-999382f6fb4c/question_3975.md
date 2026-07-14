# Q3975: handle_cat revives CAT state from a rolled-back lineage

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `handle_cat` and control CAT lineage state before and after rollback or reorg so that `WalletStateManager.handle_cat` in `chia/wallet/wallet_state_manager.py` executes a path where make `handle_cat` resurrect CAT lineage or balance state after rollback should have removed it, violating the invariant that rolled-back CAT lineage or balance state must not survive into canonical wallet state and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/wallet_state_manager.py:1228 `WalletStateManager.handle_cat`
- Entrypoint: wallet RPC or wallet sync flow reaching `handle_cat`
- Attacker controls: CAT lineage state before and after rollback or reorg
- Exploit idea: make `handle_cat` resurrect CAT lineage or balance state after rollback should have removed it
- Invariant to test: rolled-back CAT lineage or balance state must not survive into canonical wallet state
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: run a CAT reorg harness through `chia/wallet/wallet_state_manager.py:handle_cat` and assert rolled-back lineage never survives into canonical balances
