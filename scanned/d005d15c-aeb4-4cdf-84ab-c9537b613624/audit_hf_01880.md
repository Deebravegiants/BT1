# [M] Can not mint 1000 tokens, only 999

## Summary
Severity: Medium
Contest weight: 0.0144
Dataset id: 10457
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an off‑by‑one error in the token minting logic that restricts the contract to creating only 999 tokens even though the intended maximum supply is 1000. The root cause is the initialization of the internal counter that tracks minted tokens at a value of one instead of zero, combined with a check that stops minting when the counter reaches the declared limit. Because the counter starts one step ahead, the condition becomes true after 999 successful mints, preventing the final token from being minted. An attacker or any user attempting to mint the full advertised supply will be blocked at the last step, receiving a transaction failure or a silent revert. The impact is a supply shortfall: users expecting to receive the full 1000 tokens will receive only 999, which can lead to mismatched accounting, broken token economics, and loss of confidence in the protocol. This situation occurs whenever the mint function is called repeatedly until the supply cap is reached; it does not depend on external inputs beyond the number of mint calls. All participants who rely on the promised token amount—investors, liquidity providers, and downstream contracts—are affected because the actual token balance will be lower than documented. The issue was discovered during a manual code audit that compared the contract comments, which stated a limit of 1000, with the actual implementation that enforced a limit of 999. The bug is subtle because the contract still allows many mints and the failure only appears at the final iteration, making it easy to overlook during testing. To remediate the problem, the genesis counter should be initialized to zero (or the limit check should be adjusted to allow the final mint), ensuring that exactly 1000 tokens can be minted as intended. This class of bug falls under the broader category of off‑by‑one errors in supply‑capped token contracts, where an incorrect initial value or boundary condition leads to an unexpected reduction in total supply, violating the business rule that the token supply must match the advertised amount.

## Recommendation
Change genesisCounter to 0.
