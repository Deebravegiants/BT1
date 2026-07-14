# Q2385: create_nft_layer_puzzle_with_curry_params carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `create_nft_layer_puzzle_with_curry_params` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `create_nft_layer_puzzle_with_curry_params` in `chia/wallet/nft_wallet/nft_puzzle_utils.py` executes a path where make `create_nft_layer_puzzle_with_curry_params` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/nft_wallet/nft_puzzle_utils.py:34 `create_nft_layer_puzzle_with_curry_params`
- Entrypoint: wallet RPC or wallet sync flow reaching `create_nft_layer_puzzle_with_curry_params`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `create_nft_layer_puzzle_with_curry_params` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/wallet/nft_wallet/nft_puzzle_utils.py:create_nft_layer_puzzle_with_curry_params` and assert stale spend state is purged before replayed data is reconsidered
