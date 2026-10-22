# [M] Unsafe Token Transfer

## Summary
Severity: Medium
Contest weight: 0.0934
Dataset id: 5195
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the FundsLib contract, the transfer of tokens to the protocol fee recipient is performed using the standard ERC-20 transfer() function:
IERC20(asset).transfer(p.protocolFeeRecipient, protocolFeeAmount);
This approach assumes compliance with the ERC-20 speciﬁcation, including the return of a boolean success value. However, many tokens in the Ethereum ecosystem, such as USDT and others, do not strictly follow the ERC-20 standard and either do not return a value or behave inconsistently.

## Recommendation
Replace the use of IERC20(asset).transfer(...) with OpenZeppelin’s SafeERC20.safeTransfer(...), which safely handles non-compliant tokens by suppressing return value decoding and inferring success from the absence of reverts. This wrapper ensures maximum compatibility across token implementations.
