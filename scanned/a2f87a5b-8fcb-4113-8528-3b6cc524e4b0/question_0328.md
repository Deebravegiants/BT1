# Q0328: prooflessDeposit accounting via MAX_LEAVES_PD boundary with zero-amount  [across a batch of transactions]

## Question
Can an unprivileged attacker call prooflessDeposit (directly or through HinkalWrapper) using MAX_LEAVES_PD boundary with zero-amount entries filtered to bypass the amount>0 require, where amount==0 entries interact with the unique-token summation, so the on-chain commitments minted exceed the value actually transferred in, specifically across a batch of transactions landing in one block (where batching and ordering change the observable pre/post state)?

## Target
- File/function: contracts/Hinkal.sol :: prooflessDeposit / _handleTransfersFromProoflessDeposit
- Entrypoint: Hinkal.prooflessDeposit
- Attacker controls: erc20Addresses, amounts, stealthAddressStructures, msg.value, createBlockedUtxos
- Exploit idea: break the per-token balanceAfter-balanceBefore==amount check while over-minting leaves
- Invariant to test: sum of on-chain UTXO amounts minted == net value transferred into Hinkal
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: call prooflessDeposit, assert credited leaf value > vault balance delta
