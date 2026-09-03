# Q1403: prooflessDeposit accounting via address(0) with msg.value split across m [when the relay path is used wi]

## Question
Can an unprivileged attacker call prooflessDeposit (directly or through HinkalWrapper) using address(0) with msg.value split across multiple ETH entries, where _handleTransfersFromProoflessDeposit subtracts msg.value only once per unique token, so the on-chain commitments minted exceed the value actually transferred in, specifically when the relay path is used with a zero effective fee (where the relay branch changes the value split)?

## Target
- File/function: contracts/Hinkal.sol :: prooflessDeposit / _handleTransfersFromProoflessDeposit
- Entrypoint: Hinkal.prooflessDeposit
- Attacker controls: erc20Addresses, amounts, stealthAddressStructures, msg.value, createBlockedUtxos
- Exploit idea: break the per-token balanceAfter-balanceBefore==amount check while over-minting leaves
- Invariant to test: sum of on-chain UTXO amounts minted == net value transferred into Hinkal
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: call prooflessDeposit, assert credited leaf value > vault balance delta
