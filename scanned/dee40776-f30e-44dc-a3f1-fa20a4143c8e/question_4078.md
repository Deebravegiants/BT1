# Q4078: prooflessDeposit accounting via a fee-on-transfer token so balanceAfter- [when onChainCreation[i] is tru]

## Question
Can an unprivileged attacker call prooflessDeposit (directly or through HinkalWrapper) using a fee-on-transfer token so balanceAfter-balanceBefore < amount reverts, then front-run to pass, where the strict equality require can be satisfied via a balance-inflating callback, so the on-chain commitments minted exceed the value actually transferred in, specifically when onChainCreation[i] is true for the affected token (where the RHS of the balance equation drops the amount term)?

## Target
- File/function: contracts/Hinkal.sol :: prooflessDeposit / _handleTransfersFromProoflessDeposit
- Entrypoint: Hinkal.prooflessDeposit
- Attacker controls: erc20Addresses, amounts, stealthAddressStructures, msg.value, createBlockedUtxos
- Exploit idea: break the per-token balanceAfter-balanceBefore==amount check while over-minting leaves
- Invariant to test: sum of on-chain UTXO amounts minted == net value transferred into Hinkal
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: call prooflessDeposit, assert credited leaf value > vault balance delta
