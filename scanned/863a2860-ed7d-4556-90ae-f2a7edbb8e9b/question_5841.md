# Q5841: balanceDif accounting with the native asset address(0) listed alongside its wrapped form via a LiFi swap external action [when the tree has exactly one ]

## Question
Can an unprivileged attacker route a LiFi swap external action using the native asset address(0) listed alongside its wrapped form, so that ETH is counted by both msg.value and an ERC20 balance, and make Hinkal.transact's post-transfer check `balanceDif == (onChainCreation ? 0 : amountChanges[i]) + utxoAmount` hold while the vault actually receives less value than the shielded UTXOs it mints, specifically when the tree has exactly one prior leaf (where roots[MINIMUM_INDEX] equals that leaf directly)?

## Target
- File/function: contracts/Hinkal.sol :: transact / ExternalActionSwap.swap
- Entrypoint: Hinkal.transact
- Attacker controls: erc20TokenAddresses, amountChanges, slippageValues, the deployed token, externalActionData
- Exploit idea: exploit that getBalancesForArray snapshots via balanceOf while ETH is counted by both msg.value and an ERC20 balance
- Invariant to test: net tokens entering Hinkal == sum(amountChanges) + sum(on-chain UTXO amounts minted)
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: deploy the token, run the tx, assert vault balance delta < credited UTXO value
