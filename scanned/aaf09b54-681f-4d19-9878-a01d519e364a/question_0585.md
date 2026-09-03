# Q0585: balanceDif accounting with a rebasing ERC20 whose balanceOf shifts within the tx via an Emporium external action [when a same-token second leg i]

## Question
Can an unprivileged attacker route an Emporium external action using a rebasing ERC20 whose balanceOf shifts within the tx, so that balanceOf changes between the pre and post snapshots, and make Hinkal.transact's post-transfer check `balanceDif == (onChainCreation ? 0 : amountChanges[i]) + utxoAmount` hold while the vault actually receives less value than the shielded UTXOs it mints, specifically when a same-token second leg is present in the same call (where the per-token loop processes that token twice)?

## Target
- File/function: contracts/Hinkal.sol :: transact / EmporiumUpgradeable.runAction
- Entrypoint: Hinkal.transact
- Attacker controls: erc20TokenAddresses, amountChanges, slippageValues, the deployed token, externalActionData
- Exploit idea: exploit that getBalancesForArray snapshots via balanceOf while balanceOf changes between the pre and post snapshots
- Invariant to test: net tokens entering Hinkal == sum(amountChanges) + sum(on-chain UTXO amounts minted)
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: deploy the token, run the tx, assert vault balance delta < credited UTXO value
