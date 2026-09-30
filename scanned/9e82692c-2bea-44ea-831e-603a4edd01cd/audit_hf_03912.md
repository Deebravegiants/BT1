# [M] Agents might not be able to prevent being liq-

## Summary
Severity: Medium
Contest weight: 0.0867
Dataset id: 20211
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Agents might not be able to prevent being liquidated (defaulted) GLIF uses a modifier isOpen to upgrade the pools and to prevent from interacting with specific functions like borrow , pay , or deposit . be in the pay function. That is basically the function were you repay your principal/borrowed amount + interest. In the case the the contracts are paused, agents will fail to pay back their borrowed amount falling in default states. Agents will fall to repay debt and they will be entering default/administration if any pool is paused and it is not being upgraded

## Recommendation
Do not use isOpen in pay()
