# [M] M-08 | AutoCompoundingPodLp Is Not EIP Compliant

## Summary
Severity: Medium
Contest weight: 0.1734
Dataset id: 22206
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Some [EIP-4626](https://eips.ethereum.org/EIPS/eip-4626) compliance issues have been observed in the AutoCompoundingPodLp contract:
1. According to EIP-4626, the mint function must mint exactly the user-inputted amount of shares, and the withdraw function must transfer exactly the specified assets amount. However, these functions mint or withdraw fewer tokens due to rounding down twice during the action flows. During the withdraw function in the codebase:
• User provides _assets amount.
• It is converted to shares with convertToShares function, which rounds down.
• Then, the internal _withdraw function is called with this shares amount.
• In this internal function, the shares amount is converted to assets again with convertToAssets, which also rounds down. As a result, the actual assets amount transferred to the user is not the same as the user-provided amount. The same issue can be observed in the mint function as well.
2. According to EIP-4626, withdraw and redeem functions must support transaction flows where the msg.sender has an approval from the owner. However, in the codebase, withdrawals and redeems can only be performed by the owner, and approved users cannot execute these actions.

## Recommendation
Update mint and withdraw functions to comply with the EIP specification and ensure the exact amounts are transferred. Also, update withdraw and redeem function to support approved users.
