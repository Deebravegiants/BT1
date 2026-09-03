# Q3803: balanceDif accounting with a double-entry token exposing two addresses for one balance via an Emporium external action [when the amount is set to the ]

## Question
Can an unprivileged attacker route an Emporium external action using a double-entry token exposing two addresses for one balance, so that two erc20TokenAddresses entries map to one real balance, and make Hinkal.transact's post-transfer check `balanceDif == (onChainCreation ? 0 : amountChanges[i]) + utxoAmount` hold while the vault actually receives less value than the shielded UTXOs it mints, specifically when the amount is set to the field-boundary near CIRCOM_P (where modular encoding of amounts is exercised)?

## Target
- File/function: contracts/Hinkal.sol :: transact / EmporiumUpgradeable.runAction
- Entrypoint: Hinkal.transact
- Attacker controls: erc20TokenAddresses, amountChanges, slippageValues, the deployed token, externalActionData
- Exploit idea: exploit that getBalancesForArray snapshots via balanceOf while two erc20TokenAddresses entries map to one real balance
- Invariant to test: net tokens entering Hinkal == sum(amountChanges) + sum(on-chain UTXO amounts minted)
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: deploy the token, run the tx, assert vault balance delta < credited UTXO value
