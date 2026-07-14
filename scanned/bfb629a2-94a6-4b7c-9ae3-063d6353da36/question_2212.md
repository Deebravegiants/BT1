# Q2212: select_smallest_coin_over_target lets crafted conflicts block valid spends for too long

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `select_smallest_coin_over_target` and control a sequence of conflicting but protocol-valid spends and arrival order so that `select_smallest_coin_over_target` in `chia/wallet/coin_selection.py` executes a path where abuse conflict handling inside `select_smallest_coin_over_target` so honest valid spends stay excluded while attacker-controlled conflicts cycle, violating the invariant that an attacker must not be able to keep honest valid spends out of processing under normal network assumptions and leading to Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions?

## Target
- File/function: chia/wallet/coin_selection.py:131 `select_smallest_coin_over_target`
- Entrypoint: wallet RPC or wallet sync flow reaching `select_smallest_coin_over_target`
- Attacker controls: a sequence of conflicting but protocol-valid spends and arrival order
- Exploit idea: abuse conflict handling inside `select_smallest_coin_over_target` so honest valid spends stay excluded while attacker-controlled conflicts cycle
- Invariant to test: an attacker must not be able to keep honest valid spends out of processing under normal network assumptions
- Expected Immunefi impact: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions
- Fast validation: fuzz conflict order into `chia/wallet/coin_selection.py:select_smallest_coin_over_target` and assert a valid honest spend eventually processes under bounded attacker traffic
