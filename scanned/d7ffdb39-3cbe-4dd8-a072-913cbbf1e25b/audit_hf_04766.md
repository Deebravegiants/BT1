# [M] Steadefi WETH vault cannot facilitate with-

## Summary
Severity: Medium
Contest weight: 0.0000
Dataset id: 22611
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability concerns a Steadefi WETH vault contract that is unable to complete a core financial operation, most likely a withdrawal or deposit, due to a logical flaw in the contract’s handling of WETH transfers. The root cause is an incorrect or missing implementation of the token transfer call, such as using an empty calldata payload, an improper interface, or a faulty condition that always reverts the call. Because the vault relies on this transfer to move WETH in or out of the contract, the failure prevents users from retrieving their deposited assets. An attacker or any user attempting to withdraw will see the transaction succeed on-chain but receive no tokens, resulting in a balance that appears unchanged or zero on the user interface. The impact is that funds become effectively locked in the vault, breaking the accounting assumptions of the protocol that deposited amounts are always withdrawable. This condition manifests whenever a user initiates a withdrawal (or deposit) request; the contract executes the transfer logic, encounters the flawed call, and either reverts silently or completes without moving tokens. The issue was discovered during a manual audit where the auditor attempted to simulate a withdrawal and observed that the vault did not transfer any WETH despite emitting a successful event. The bug is subtle because the contract may still emit expected events and update internal accounting, giving the impression that the operation succeeded, while the external token balance remains unchanged. To remediate, the contract should correctly invoke the WETH token’s transfer or withdraw function with proper calldata, ensure that return values are checked, and remove any unconditional revert paths that block token movement. In broader terms, this is a classic example of a token transfer mis‑implementation that leads to funds disappearing from the user’s perspective, violating the protocol’s financial guarantees and user expectations of receiving their assets back on demand.

## Recommendation
No recommendation available
