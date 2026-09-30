# [M] M-01 | Risk Of Function Selector And Storage Collision

## Summary
Severity: Medium
Contest weight: 0.0442
Dataset id: 20853
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a storage and function selector collision in the BlastOnboarding contract, which acts as a proxy but also declares its own state variables and functions. Because a proxy is expected to forward calls to an implementation contract and keep only a minimal set of storage slots, any additional variables in the proxy occupy slots that the implementation also expects to use. Likewise, if the proxy defines functions whose 4‑byte selectors match those of functions in the implementation, the proxy will intercept calls that were meant for the implementation. An attacker can exploit this by invoking a function that appears to belong to the logic contract; the proxy’s own version will be executed, potentially reading or writing to a storage slot that controls critical parameters such as admin address or fund balances. This can lead to unauthorized upgrades, loss of control over the contract, or misdirection of funds. The issue manifests when a bootstrapper (logic) contract is deployed behind the BlastOnboarding proxy and its selector set overlaps with the proxy’s functions, or when the implementation expects storage slots that the proxy has already occupied. All participants that rely on the onboarding process – the protocol, its users, and any funds held during the onboarding phase – are at risk. The problem was discovered during a manual audit that compared the proxy’s storage layout and function signatures with those of typical implementation contracts and noticed the mismatch. Because the proxy still appears functional and the collisions do not raise compile‑time errors, the bug can remain hidden until a specific function call triggers the wrong code path. The recommended remediation is to redesign the proxy so that it contains only the essential storage (e.g., implementation address) using reserved or unstructured slots, and to ensure that no function in the proxy shares a selector with any function in the implementation. A systematic verification of selector uniqueness and storage slot allocation should be performed before any future bootstrapper is linked to the proxy.

## Recommendation
Any bootstrapper implementation that is used in the future should be rigorously veriﬁed to have no collisions with the existing function selectors or storage slots in the BlastOnboarding contract.
