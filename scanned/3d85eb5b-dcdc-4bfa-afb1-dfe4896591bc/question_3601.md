# Q3601: balanceDif accounting with a fee-on-transfer ERC20 you deployed via an internal transact (externalActionId == 0) [when the amount is set to the ]

## Question
Can an unprivileged attacker route an internal transact (externalActionId == 0) using a fee-on-transfer ERC20 you deployed, so that the transfer delivers fewer tokens than the amount argument, and make Hinkal.transact's post-transfer check `balanceDif == (onChainCreation ? 0 : amountChanges[i]) + utxoAmount` hold while the vault actually receives less value than the shielded UTXOs it mints, specifically when the amount is set to the field-boundary near CIRCOM_P (where modular encoding of amounts is exercised)?

## Target
- File/function: contracts/Hinkal.sol :: transact / Hinkal._internalTransact
- Entrypoint: Hinkal.transact
- Attacker controls: erc20TokenAddresses, amountChanges, slippageValues, the deployed token, externalActionData
- Exploit idea: exploit that getBalancesForArray snapshots via balanceOf while the transfer delivers fewer tokens than the amount argument
- Invariant to test: net tokens entering Hinkal == sum(amountChanges) + sum(on-chain UTXO amounts minted)
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: deploy the token, run the tx, assert vault balance delta < credited UTXO value
