# Q3113: generate_signed_transaction revives CAT state from a rolled-back lineage

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `generate_signed_transaction` and control CAT lineage state before and after rollback or reorg so that `CRCATWallet.generate_signed_transaction` in `chia/wallet/vc_wallet/cr_cat_wallet.py` executes a path where make `generate_signed_transaction` resurrect CAT lineage or balance state after rollback should have removed it, violating the invariant that rolled-back CAT lineage or balance state must not survive into canonical wallet state and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/vc_wallet/cr_cat_wallet.py:594 `CRCATWallet.generate_signed_transaction`
- Entrypoint: wallet RPC or wallet sync flow reaching `generate_signed_transaction`
- Attacker controls: CAT lineage state before and after rollback or reorg
- Exploit idea: make `generate_signed_transaction` resurrect CAT lineage or balance state after rollback should have removed it
- Invariant to test: rolled-back CAT lineage or balance state must not survive into canonical wallet state
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: run a CAT reorg harness through `chia/wallet/vc_wallet/cr_cat_wallet.py:generate_signed_transaction` and assert rolled-back lineage never survives into canonical balances
