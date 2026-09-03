# Q2474: balanceDif accounting with a token that reverts on zero-value transfer via a prooflessDeposit call [when the same proof is reused ]

## Question
Can an unprivileged attacker route a prooflessDeposit call using a token that reverts on zero-value transfer, so that a zero-amount leg strands the whole batch, and make Hinkal.transact's post-transfer check `balanceDif == (onChainCreation ? 0 : amountChanges[i]) + utxoAmount` hold while the vault actually receives less value than the shielded UTXOs it mints, specifically when the same proof is reused with only calldata mutated (where the proof-to-calldata binding is stressed)?

## Target
- File/function: contracts/Hinkal.sol :: transact / Hinkal.prooflessDeposit
- Entrypoint: Hinkal.transact
- Attacker controls: erc20TokenAddresses, amountChanges, slippageValues, the deployed token, externalActionData
- Exploit idea: exploit that getBalancesForArray snapshots via balanceOf while a zero-amount leg strands the whole batch
- Invariant to test: net tokens entering Hinkal == sum(amountChanges) + sum(on-chain UTXO amounts minted)
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: deploy the token, run the tx, assert vault balance delta < credited UTXO value
