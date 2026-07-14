# Q2228: create_graftroot_offer_puz allows stale offer intent to settle against fresh state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `create_graftroot_offer_puz` and control previously valid offer blobs replayed after wallet state changed so that `create_graftroot_offer_puz` in `chia/wallet/db_wallet/db_wallet_puzzles.py` executes a path where reuse stale offer payloads in `create_graftroot_offer_puz` after the referenced wallet state moved on, violating the invariant that an old offer payload must not settle once the underlying spendable state has materially changed and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/db_wallet/db_wallet_puzzles.py:79 `create_graftroot_offer_puz`
- Entrypoint: wallet RPC or wallet sync flow reaching `create_graftroot_offer_puz`
- Attacker controls: previously valid offer blobs replayed after wallet state changed
- Exploit idea: reuse stale offer payloads in `create_graftroot_offer_puz` after the referenced wallet state moved on
- Invariant to test: an old offer payload must not settle once the underlying spendable state has materially changed
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: replay a formerly valid offer through `chia/wallet/db_wallet/db_wallet_puzzles.py:create_graftroot_offer_puz` after wallet state changes and assert settlement is rejected
