# Q3068: create_from_puzzle_info revives CAT state from a rolled-back lineage

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `create_from_puzzle_info` and control CAT lineage state before and after rollback or reorg so that `CRCATWallet.create_from_puzzle_info` in `chia/wallet/vc_wallet/cr_cat_wallet.py` executes a path where make `create_from_puzzle_info` resurrect CAT lineage or balance state after rollback should have removed it, violating the invariant that rolled-back CAT lineage or balance state must not survive into canonical wallet state and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/vc_wallet/cr_cat_wallet.py:130 `CRCATWallet.create_from_puzzle_info`
- Entrypoint: wallet RPC or wallet sync flow reaching `create_from_puzzle_info`
- Attacker controls: CAT lineage state before and after rollback or reorg
- Exploit idea: make `create_from_puzzle_info` resurrect CAT lineage or balance state after rollback should have removed it
- Invariant to test: rolled-back CAT lineage or balance state must not survive into canonical wallet state
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: run a CAT reorg harness through `chia/wallet/vc_wallet/cr_cat_wallet.py:create_from_puzzle_info` and assert rolled-back lineage never survives into canonical balances
