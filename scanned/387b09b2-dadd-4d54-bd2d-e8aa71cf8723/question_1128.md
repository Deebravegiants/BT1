# Q1128: prooflessDeposit accounting via duplicate token addresses in erc20Addres [when the ETH (address(0)) leg ]

## Question
Can an unprivileged attacker call prooflessDeposit (directly or through HinkalWrapper) using duplicate token addresses in erc20Addresses summed into one balanceAfter check, where performProoflessDepositChecks never enforces distinct tokens as the circuit does, so the on-chain commitments minted exceed the value actually transferred in, specifically when the ETH (address(0)) leg is present alongside (where the msg.value branch adds a second accounting path)?

## Target
- File/function: contracts/Hinkal.sol :: prooflessDeposit / _handleTransfersFromProoflessDeposit
- Entrypoint: Hinkal.prooflessDeposit
- Attacker controls: erc20Addresses, amounts, stealthAddressStructures, msg.value, createBlockedUtxos
- Exploit idea: break the per-token balanceAfter-balanceBefore==amount check while over-minting leaves
- Invariant to test: sum of on-chain UTXO amounts minted == net value transferred into Hinkal
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: call prooflessDeposit, assert credited leaf value > vault balance delta
