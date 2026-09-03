# Q4270: balanceDif accounting with a token that reverts on zero-value transfer via an internal transact (externalActionId == 0) [when onChainCreation[i] is tru]

## Question
Can an unprivileged attacker route an internal transact (externalActionId == 0) using a token that reverts on zero-value transfer, so that a zero-amount leg strands the whole batch, and make Hinkal.transact's post-transfer check `balanceDif == (onChainCreation ? 0 : amountChanges[i]) + utxoAmount` hold while the vault actually receives less value than the shielded UTXOs it mints, specifically when onChainCreation[i] is true for the affected token (where the RHS of the balance equation drops the amount term)?

## Target
- File/function: contracts/Hinkal.sol :: transact / Hinkal._internalTransact
- Entrypoint: Hinkal.transact
- Attacker controls: erc20TokenAddresses, amountChanges, slippageValues, the deployed token, externalActionData
- Exploit idea: exploit that getBalancesForArray snapshots via balanceOf while a zero-amount leg strands the whole batch
- Invariant to test: net tokens entering Hinkal == sum(amountChanges) + sum(on-chain UTXO amounts minted)
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: deploy the token, run the tx, assert vault balance delta < credited UTXO value
