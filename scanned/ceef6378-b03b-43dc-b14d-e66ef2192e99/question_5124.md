# Q5124: balanceDif accounting with a token whose balanceOf you can inflate via a self-transfer callback via an Emporium external action [when routed through HinkalWrap]

## Question
Can an unprivileged attacker route an Emporium external action using a token whose balanceOf you can inflate via a self-transfer callback, so that balanceOf reads high only during the post snapshot, and make Hinkal.transact's post-transfer check `balanceDif == (onChainCreation ? 0 : amountChanges[i]) + utxoAmount` hold while the vault actually receives less value than the shielded UTXOs it mints, specifically when routed through HinkalWrapper's fee settlement first (where an extra value hop precedes Hinkal)?

## Target
- File/function: contracts/Hinkal.sol :: transact / EmporiumUpgradeable.runAction
- Entrypoint: Hinkal.transact
- Attacker controls: erc20TokenAddresses, amountChanges, slippageValues, the deployed token, externalActionData
- Exploit idea: exploit that getBalancesForArray snapshots via balanceOf while balanceOf reads high only during the post snapshot
- Invariant to test: net tokens entering Hinkal == sum(amountChanges) + sum(on-chain UTXO amounts minted)
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: deploy the token, run the tx, assert vault balance delta < credited UTXO value
