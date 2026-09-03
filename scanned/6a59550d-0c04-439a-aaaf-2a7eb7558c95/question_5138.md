# Q5138: balanceDif accounting with a token that returns false instead of reverting on transfer via a LiFi swap external action [when routed through HinkalWrap]

## Question
Can an unprivileged attacker route a LiFi swap external action using a token that returns false instead of reverting on transfer, so that SafeERC20 handling and the balance delta disagree, and make Hinkal.transact's post-transfer check `balanceDif == (onChainCreation ? 0 : amountChanges[i]) + utxoAmount` hold while the vault actually receives less value than the shielded UTXOs it mints, specifically when routed through HinkalWrapper's fee settlement first (where an extra value hop precedes Hinkal)?

## Target
- File/function: contracts/Hinkal.sol :: transact / ExternalActionSwap.swap
- Entrypoint: Hinkal.transact
- Attacker controls: erc20TokenAddresses, amountChanges, slippageValues, the deployed token, externalActionData
- Exploit idea: exploit that getBalancesForArray snapshots via balanceOf while SafeERC20 handling and the balance delta disagree
- Invariant to test: net tokens entering Hinkal == sum(amountChanges) + sum(on-chain UTXO amounts minted)
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: deploy the token, run the tx, assert vault balance delta < credited UTXO value
