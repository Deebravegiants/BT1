# Q1469: prooflessDeposit accounting via createBlockedUtxos true to emit BlockedU [when the relay path is used wi]

## Question
Can an unprivileged attacker call prooflessDeposit (directly or through HinkalWrapper) using createBlockedUtxos true to emit BlockedUtxosCreated while minting spendable leaves, where the blocked flag is only an event with no on-chain enforcement, so the on-chain commitments minted exceed the value actually transferred in, specifically when the relay path is used with a zero effective fee (where the relay branch changes the value split)?

## Target
- File/function: contracts/Hinkal.sol :: prooflessDeposit / _handleTransfersFromProoflessDeposit
- Entrypoint: Hinkal.prooflessDeposit
- Attacker controls: erc20Addresses, amounts, stealthAddressStructures, msg.value, createBlockedUtxos
- Exploit idea: break the per-token balanceAfter-balanceBefore==amount check while over-minting leaves
- Invariant to test: sum of on-chain UTXO amounts minted == net value transferred into Hinkal
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: call prooflessDeposit, assert credited leaf value > vault balance delta
