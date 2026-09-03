# Q0669: balanceDif accounting with the native asset address(0) listed alongside its wrapped form via a HinkalWrapper.prooflessDeposit call [when a same-token second leg i]

## Question
Can an unprivileged attacker route a HinkalWrapper.prooflessDeposit call using the native asset address(0) listed alongside its wrapped form, so that ETH is counted by both msg.value and an ERC20 balance, and make Hinkal.transact's post-transfer check `balanceDif == (onChainCreation ? 0 : amountChanges[i]) + utxoAmount` hold while the vault actually receives less value than the shielded UTXOs it mints, specifically when a same-token second leg is present in the same call (where the per-token loop processes that token twice)?

## Target
- File/function: contracts/Hinkal.sol :: transact / HinkalWrapper.prooflessDeposit
- Entrypoint: Hinkal.transact
- Attacker controls: erc20TokenAddresses, amountChanges, slippageValues, the deployed token, externalActionData
- Exploit idea: exploit that getBalancesForArray snapshots via balanceOf while ETH is counted by both msg.value and an ERC20 balance
- Invariant to test: net tokens entering Hinkal == sum(amountChanges) + sum(on-chain UTXO amounts minted)
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: deploy the token, run the tx, assert vault balance delta < credited UTXO value
