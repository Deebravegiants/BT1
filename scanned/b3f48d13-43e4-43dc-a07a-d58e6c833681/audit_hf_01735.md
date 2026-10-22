# [H] MJR-2 Fix gas cost ETH transfer

## Summary
Severity: High
Contest weight: 0.0123
Dataset id: 9504
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability originates from the use of a fixed 2300‑gas stipend when transferring Ether, typically via Solidity's transfer or send functions. This design assumes that the recipient’s fallback or receive function will always fit within the limited gas amount, an assumption that was valid before certain protocol upgrades but is no longer reliable. After hard forks such as Istanbul, the gas cost of several opcodes increased, meaning that even a simple fallback may now exceed the 2300‑gas limit. When the contract attempts to send ETH using this fixed stipend, the call can run out of gas and revert, causing the transfer to fail. An attacker can exploit this by deploying a contract with a fallback that deliberately consumes more than 2300 gas, causing any ETH sent to it via transfer to revert and effectively locking the funds in the sending contract. The impact is that users expecting to receive a refund, withdrawal, or any ETH payment may see no change in their balance, experience transaction reverts, or observe that their deposited funds remain stuck. This situation occurs whenever the contract sends ETH to an address that is a contract with a non‑trivial fallback, or when network gas costs rise beyond the hard‑coded limit. All participants who interact with the contract – depositors, withdrawers, and the protocol itself – are affected because the business logic that assumes successful ETH transfers no longer holds. The issue was discovered during a manual audit that flagged the hard‑coded gas amount as a potential future failure point. It can be hard to notice because the code compiles without warnings and the transfer appears to succeed in simple test cases; only when the recipient’s fallback grows or gas costs change does the failure surface. To remediate, the contract should replace transfer/send with a low‑level call that forwards all available gas (or a configurable amount) and explicitly checks the returned success flag, handling failures gracefully. This change aligns the contract with the modern best practice of using call for ETH transfers, eliminating the fixed‑gas limitation and restoring reliable fund movement.

## Recommendation
We recommend sending ETH via call.
