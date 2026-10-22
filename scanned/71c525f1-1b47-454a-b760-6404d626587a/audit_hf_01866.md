# [M] M-11 Incorrect usage of permit

## Summary
Severity: Medium
Contest weight: 0.0396
Dataset id: 10396
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the depositTokensWithPermit function of the escrow contract, where the permit operation is executed with an amount that does not match the value originally signed by the token holder. A user signs an EIP‑2612 permit for a specific _amount, expecting the contract to forward that exact amount to the token’s permit function. However, the implementation overwrites or otherwise changes the variable used in the permit call before it is passed to the token contract, causing a mismatch between the signed allowance and the amount supplied to the permit method. Because the permit verification checks that the allowance granted by the signature equals the amount argument, the call reverts when the values differ. This mismatch can be triggered whenever a depositor invokes depositTokensWithPermit with a signed permit, making the transaction fail and the deposit not recorded. The impact is that legitimate users are unable to deposit tokens via the gas‑less permit flow, leading to failed transactions, wasted gas fees, and potential loss of confidence in the escrow service. The issue is discovered during a manual audit by MixBytes, where the code path was traced and the inconsistent use of the amount variable was identified. It is subtle because the contract compiles without errors and the revert only occurs at runtime, appearing as a generic “permit failed” error without indicating the underlying mismatch. The bug belongs to the class of incorrect parameter usage in signature‑based authorisation, where a signed value is not consistently applied throughout the workflow, violating the accounting assumption that the signed allowance equals the transferred amount. To remediate, the contract should retain the original _amount supplied by the user and pass that exact value to the token’s permit function, ensuring that the signed allowance and the amount argument are identical. This change restores the intended behaviour where a user’s signed permit reliably authorises the exact token amount to be transferred into the escrow, eliminating unexpected reverts and preserving user funds.

## Recommendation
We recommend using the initial _amount value for the permit call.
