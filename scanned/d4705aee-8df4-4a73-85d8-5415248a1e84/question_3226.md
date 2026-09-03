# Q3226: balanceDif accounting with a fee-on-transfer ERC20 you deployed via a DepositOnChainUtxos external action [when the token silently return]

## Question
Can an unprivileged attacker route a DepositOnChainUtxos external action using a fee-on-transfer ERC20 you deployed, so that the transfer delivers fewer tokens than the amount argument, and make Hinkal.transact's post-transfer check `balanceDif == (onChainCreation ? 0 : amountChanges[i]) + utxoAmount` hold while the vault actually receives less value than the shielded UTXOs it mints, specifically when the token silently returns false on failure (where SafeERC20 and the balance delta can disagree)?

## Target
- File/function: contracts/Hinkal.sol :: transact / DepositOnChainUtxosExternalAction.runAction
- Entrypoint: Hinkal.transact
- Attacker controls: erc20TokenAddresses, amountChanges, slippageValues, the deployed token, externalActionData
- Exploit idea: exploit that getBalancesForArray snapshots via balanceOf while the transfer delivers fewer tokens than the amount argument
- Invariant to test: net tokens entering Hinkal == sum(amountChanges) + sum(on-chain UTXO amounts minted)
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: deploy the token, run the tx, assert vault balance delta < credited UTXO value
