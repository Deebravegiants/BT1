# Q2160: remove_lineage revives CAT state from a rolled-back lineage

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `remove_lineage` and control CAT lineage state before and after rollback or reorg so that `CATWallet.remove_lineage` in `chia/wallet/cat_wallet/cat_wallet.py` executes a path where make `remove_lineage` resurrect CAT lineage or balance state after rollback should have removed it, violating the invariant that rolled-back CAT lineage or balance state must not survive into canonical wallet state and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/cat_wallet/cat_wallet.py:815 `CATWallet.remove_lineage`
- Entrypoint: wallet RPC or wallet sync flow reaching `remove_lineage`
- Attacker controls: CAT lineage state before and after rollback or reorg
- Exploit idea: make `remove_lineage` resurrect CAT lineage or balance state after rollback should have removed it
- Invariant to test: rolled-back CAT lineage or balance state must not survive into canonical wallet state
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: run a CAT reorg harness through `chia/wallet/cat_wallet/cat_wallet.py:remove_lineage` and assert rolled-back lineage never survives into canonical balances
