# Q0379: balanceDif accounting with an ERC777 token with a tokensReceived hook via an internal transact (externalActionId == 0) [across a batch of transactions]

## Question
Can an unprivileged attacker route an internal transact (externalActionId == 0) using an ERC777 token with a tokensReceived hook, so that the hook re-enters Hinkal during the transfer, and make Hinkal.transact's post-transfer check `balanceDif == (onChainCreation ? 0 : amountChanges[i]) + utxoAmount` hold while the vault actually receives less value than the shielded UTXOs it mints, specifically across a batch of transactions landing in one block (where batching and ordering change the observable pre/post state)?

## Target
- File/function: contracts/Hinkal.sol :: transact / Hinkal._internalTransact
- Entrypoint: Hinkal.transact
- Attacker controls: erc20TokenAddresses, amountChanges, slippageValues, the deployed token, externalActionData
- Exploit idea: exploit that getBalancesForArray snapshots via balanceOf while the hook re-enters Hinkal during the transfer
- Invariant to test: net tokens entering Hinkal == sum(amountChanges) + sum(on-chain UTXO amounts minted)
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: deploy the token, run the tx, assert vault balance delta < credited UTXO value
