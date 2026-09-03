# Q3878: prooflessDeposit accounting via address(0) with msg.value split across m [when amountChanges[i] is exact]

## Question
Can an unprivileged attacker call prooflessDeposit (directly or through HinkalWrapper) using address(0) with msg.value split across multiple ETH entries, where _handleTransfersFromProoflessDeposit subtracts msg.value only once per unique token, so the on-chain commitments minted exceed the value actually transferred in, specifically when amountChanges[i] is exactly zero for the affected token (where the zero branch skips value movement)?

## Target
- File/function: contracts/Hinkal.sol :: prooflessDeposit / _handleTransfersFromProoflessDeposit
- Entrypoint: Hinkal.prooflessDeposit
- Attacker controls: erc20Addresses, amounts, stealthAddressStructures, msg.value, createBlockedUtxos
- Exploit idea: break the per-token balanceAfter-balanceBefore==amount check while over-minting leaves
- Invariant to test: sum of on-chain UTXO amounts minted == net value transferred into Hinkal
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: call prooflessDeposit, assert credited leaf value > vault balance delta
