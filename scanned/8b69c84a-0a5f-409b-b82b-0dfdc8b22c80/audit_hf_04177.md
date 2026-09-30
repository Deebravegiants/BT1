# [M] M-05 | Disabled Native Yield Tokens Cause Loss Of Funds

## Summary
Severity: Medium
Contest weight: 0.1228
Dataset id: 20858
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If the owner does not want to enable native yield for a token with function setTokenEnabled, that token will have the default mode which is AUTOMATIC for WETH and USDB. When a token is in AUTOMATIC mode, the balance of the token in the contract increases as yield is gained. However, the DegenBox contract is unable to support rebasing tokens: /// @notice The BentoBox is a vault for tokens. The stored tokens can be ﬂash loaned and used in strategies. /// Yield from this will go to the token depositors. /// Rebasing tokens ARE NOT supported and WILL cause loss of funds. /// Any funds transfered directly onto the BentoBox will be lost, use the deposit function instead. As per the comment above, rebasing tokens are not compatible with the DegenBox and will cause loss of funds.

## Recommendation
Consider adding feature that allows the owner to set token yield mode to VOID to ensure compatibility when the owner does not want token yield enabled.
