# Q3565: balanceDif accounting with a token that returns false instead of reverting on transfer via a DepositOnChainUtxos external action [when the attacker sandwiches t]

## Question
Can an unprivileged attacker route a DepositOnChainUtxos external action using a token that returns false instead of reverting on transfer, so that SafeERC20 handling and the balance delta disagree, and make Hinkal.transact's post-transfer check `balanceDif == (onChainCreation ? 0 : amountChanges[i]) + utxoAmount` hold while the vault actually receives less value than the shielded UTXOs it mints, specifically when the attacker sandwiches the tx with their own deposit and withdraw (where surrounding state is attacker-tuned)?

## Target
- File/function: contracts/Hinkal.sol :: transact / DepositOnChainUtxosExternalAction.runAction
- Entrypoint: Hinkal.transact
- Attacker controls: erc20TokenAddresses, amountChanges, slippageValues, the deployed token, externalActionData
- Exploit idea: exploit that getBalancesForArray snapshots via balanceOf while SafeERC20 handling and the balance delta disagree
- Invariant to test: net tokens entering Hinkal == sum(amountChanges) + sum(on-chain UTXO amounts minted)
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: deploy the token, run the tx, assert vault balance delta < credited UTXO value
