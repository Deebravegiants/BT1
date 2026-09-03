# Q4929: balanceDif accounting with a double-entry token exposing two addresses for one balance via a LiFi swap external action [when the deposit uses proofles]

## Question
Can an unprivileged attacker route a LiFi swap external action using a double-entry token exposing two addresses for one balance, so that two erc20TokenAddresses entries map to one real balance, and make Hinkal.transact's post-transfer check `balanceDif == (onChainCreation ? 0 : amountChanges[i]) + utxoAmount` hold while the vault actually receives less value than the shielded UTXOs it mints, specifically when the deposit uses prooflessDeposit instead of a proof (where the no-proof mint path is taken)?

## Target
- File/function: contracts/Hinkal.sol :: transact / ExternalActionSwap.swap
- Entrypoint: Hinkal.transact
- Attacker controls: erc20TokenAddresses, amountChanges, slippageValues, the deployed token, externalActionData
- Exploit idea: exploit that getBalancesForArray snapshots via balanceOf while two erc20TokenAddresses entries map to one real balance
- Invariant to test: net tokens entering Hinkal == sum(amountChanges) + sum(on-chain UTXO amounts minted)
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: deploy the token, run the tx, assert vault balance delta < credited UTXO value
