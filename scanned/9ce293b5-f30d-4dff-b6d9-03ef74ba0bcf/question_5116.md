# Q5116: balanceDif accounting with an ERC777 token with a tokensReceived hook via a prooflessDeposit call [when routed through HinkalWrap]

## Question
Can an unprivileged attacker route a prooflessDeposit call using an ERC777 token with a tokensReceived hook, so that the hook re-enters Hinkal during the transfer, and make Hinkal.transact's post-transfer check `balanceDif == (onChainCreation ? 0 : amountChanges[i]) + utxoAmount` hold while the vault actually receives less value than the shielded UTXOs it mints, specifically when routed through HinkalWrapper's fee settlement first (where an extra value hop precedes Hinkal)?

## Target
- File/function: contracts/Hinkal.sol :: transact / Hinkal.prooflessDeposit
- Entrypoint: Hinkal.transact
- Attacker controls: erc20TokenAddresses, amountChanges, slippageValues, the deployed token, externalActionData
- Exploit idea: exploit that getBalancesForArray snapshots via balanceOf while the hook re-enters Hinkal during the transfer
- Invariant to test: net tokens entering Hinkal == sum(amountChanges) + sum(on-chain UTXO amounts minted)
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: deploy the token, run the tx, assert vault balance delta < credited UTXO value
