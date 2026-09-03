# Q5776: balanceDif accounting with a rebasing ERC20 whose balanceOf shifts within the tx via a HinkalWrapper.prooflessDeposit call [when the tree has exactly one ]

## Question
Can an unprivileged attacker route a HinkalWrapper.prooflessDeposit call using a rebasing ERC20 whose balanceOf shifts within the tx, so that balanceOf changes between the pre and post snapshots, and make Hinkal.transact's post-transfer check `balanceDif == (onChainCreation ? 0 : amountChanges[i]) + utxoAmount` hold while the vault actually receives less value than the shielded UTXOs it mints, specifically when the tree has exactly one prior leaf (where roots[MINIMUM_INDEX] equals that leaf directly)?

## Target
- File/function: contracts/Hinkal.sol :: transact / HinkalWrapper.prooflessDeposit
- Entrypoint: Hinkal.transact
- Attacker controls: erc20TokenAddresses, amountChanges, slippageValues, the deployed token, externalActionData
- Exploit idea: exploit that getBalancesForArray snapshots via balanceOf while balanceOf changes between the pre and post snapshots
- Invariant to test: net tokens entering Hinkal == sum(amountChanges) + sum(on-chain UTXO amounts minted)
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: deploy the token, run the tx, assert vault balance delta < credited UTXO value
