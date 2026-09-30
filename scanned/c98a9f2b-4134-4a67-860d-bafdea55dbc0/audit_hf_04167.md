# [H] H-01 | Weth Transferred From The Wrong Address

## Summary
Severity: High
Contest weight: 0.1133
Dataset id: 20848
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Router.createPoolETH function, a deposit to the weth contract is made but then a subsequent weth safeTransferFrom is made from the msg.sender to the newly created pool. As a result, users may accidentally pay twice for the WETH the pool should be created with if they had approved the Router contract. The native Ether sent to the Router will be lost.

## Recommendation
Use the weth safeTransferFrom to transfer from the Router contract to the newly created pool rather than from the msg.sender.
