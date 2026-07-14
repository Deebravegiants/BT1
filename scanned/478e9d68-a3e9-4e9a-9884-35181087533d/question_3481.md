# Q3481: validate_block_inclusion mishandles compact or summarized proof substitution

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `validate_block_inclusion` and control compact proofs, summarized state, and full-object substitution timing so that `WalletNode.validate_block_inclusion` in `chia/wallet/wallet_node.py` executes a path where swap compact or summarized proof material into `validate_block_inclusion` so it stands in for a stronger object than intended, violating the invariant that compact or summarized proofs must never stand in for stronger proof objects without equivalent validation and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/wallet_node.py:1646 `WalletNode.validate_block_inclusion`
- Entrypoint: wallet RPC or wallet sync flow reaching `validate_block_inclusion`
- Attacker controls: compact proofs, summarized state, and full-object substitution timing
- Exploit idea: swap compact or summarized proof material into `validate_block_inclusion` so it stands in for a stronger object than intended
- Invariant to test: compact or summarized proofs must never stand in for stronger proof objects without equivalent validation
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: swap compact versus full proof objects into `chia/wallet/wallet_node.py:validate_block_inclusion` and assert summarized forms never bypass equivalent validation
