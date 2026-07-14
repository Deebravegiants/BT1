# Q2173: add_lineage_proof mixes CAT accounting with XCH or offer settlement state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_lineage_proof` and control CAT-to-XCH settlement inputs, multi-asset specs, and spend ordering so that `CATLineageStore.add_lineage_proof` in `chia/wallet/cat_wallet/lineage_store.py` executes a path where make `add_lineage_proof` settle CAT and XCH legs under mismatched accounting assumptions, violating the invariant that CAT settlement must not create or destroy value when crossing XCH, CAT, and offer bookkeeping and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/cat_wallet/lineage_store.py:32 `CATLineageStore.add_lineage_proof`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_lineage_proof`
- Attacker controls: CAT-to-XCH settlement inputs, multi-asset specs, and spend ordering
- Exploit idea: make `add_lineage_proof` settle CAT and XCH legs under mismatched accounting assumptions
- Invariant to test: CAT settlement must not create or destroy value when crossing XCH, CAT, and offer bookkeeping
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: settle CAT/XCH offers with crafted discrepancy inputs and assert `chia/wallet/cat_wallet/lineage_store.py:add_lineage_proof` preserves total value and asset identity
