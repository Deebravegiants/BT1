# [M] address.transfer is used in the codebase, which could lead to stuck funds

## Summary
Severity: Medium
Contest weight: 0.0544
Dataset id: 11104
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability stems from the use of the Solidity built‑in address.transfer function to move Ether out of the contract. Transfer forwards a fixed stipend of 2300 gas to the recipient’s fallback or receive function. This hard‑coded gas limit was safe when the EVM required very little gas for simple operations, but subsequent protocol upgrades (for example EIP‑1884) increased the cost of certain opcodes, and many modern smart‑contract wallets implement fallback logic that consumes more than 2300 gas. Consequently, when the contract attempts to send Ether to such an address, the call runs out of gas, the transfer reverts, and the execution path that should release the funds is aborted. The result is that the Ether intended for the user or for a downstream protocol remains locked inside the contract, effectively disappearing from the user’s perspective. Users expect a successful withdrawal or refund, but instead see no change in their balance, receive no transaction receipt of a transfer, or encounter a failed transaction that leaves the contract’s internal accounting out of sync. The issue manifests whenever the codebase uses address.transfer to pay arbitrary addresses – especially external contracts or newly created wallet contracts – without checking the recipient’s gas requirements. It also becomes more likely after network upgrades that raise the gas cost of storage reads or other operations used in fallback functions. The problem was identified during a manual security audit that flagged the use of transfer as a known anti‑pattern. It can be hard to notice because the failure occurs only for certain recipients; normal EOAs with empty fallback functions still succeed, giving a false sense of safety. The bug belongs to the class of “gas‑stipend transfer failures” that lead to stuck funds and broken accounting assumptions. To remediate, the contract should replace address.transfer with a low‑level call, e.g. address.call{value:amount}(''), optionally specifying a higher gas limit, and must verify the returned boolean to handle failures gracefully. A pull‑payment pattern or an adjustable‑gas forwarding mechanism can ensure that funds are not unintentionally locked and that the protocol’s financial guarantees remain intact.

## Recommendation
Use address.call{value: amount}("") instead, here is an example implementation. If the gas usage of the target is a concern, this implementation can be used instead, setting the _gas to some amount that may be changed and _maxCopy and _calldata to 0.
