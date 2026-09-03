# Q5294: prooflessDeposit accounting via createBlockedUtxos true to emit BlockedU [when the external action is Em]

## Question
Can an unprivileged attacker call prooflessDeposit (directly or through HinkalWrapper) using createBlockedUtxos true to emit BlockedUtxosCreated while minting spendable leaves, where the blocked flag is only an event with no on-chain enforcement, so the on-chain commitments minted exceed the value actually transferred in, specifically when the external action is Emporium with signerAddress zero (where the unsigned stateless op path runs)?

## Target
- File/function: contracts/Hinkal.sol :: prooflessDeposit / _handleTransfersFromProoflessDeposit
- Entrypoint: Hinkal.prooflessDeposit
- Attacker controls: erc20Addresses, amounts, stealthAddressStructures, msg.value, createBlockedUtxos
- Exploit idea: break the per-token balanceAfter-balanceBefore==amount check while over-minting leaves
- Invariant to test: sum of on-chain UTXO amounts minted == net value transferred into Hinkal
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: call prooflessDeposit, assert credited leaf value > vault balance delta
