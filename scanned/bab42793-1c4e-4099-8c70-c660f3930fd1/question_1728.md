# Q1728: create_full_puzzle lets crafted conflicts block valid spends for too long

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `create_full_puzzle` and control a sequence of conflicting but protocol-valid spends and arrival order so that `create_full_puzzle` in `chia/pools/pool_puzzles.py` executes a path where abuse conflict handling inside `create_full_puzzle` so honest valid spends stay excluded while attacker-controlled conflicts cycle, violating the invariant that an attacker must not be able to keep honest valid spends out of processing under normal network assumptions and leading to Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions?

## Target
- File/function: chia/pools/pool_puzzles.py:87 `create_full_puzzle`
- Entrypoint: pool wallet or singleton spend flow reaching `create_full_puzzle`
- Attacker controls: a sequence of conflicting but protocol-valid spends and arrival order
- Exploit idea: abuse conflict handling inside `create_full_puzzle` so honest valid spends stay excluded while attacker-controlled conflicts cycle
- Invariant to test: an attacker must not be able to keep honest valid spends out of processing under normal network assumptions
- Expected Immunefi impact: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions
- Fast validation: fuzz conflict order into `chia/pools/pool_puzzles.py:create_full_puzzle` and assert a valid honest spend eventually processes under bounded attacker traffic
