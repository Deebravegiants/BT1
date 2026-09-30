# [H] MJR-14 Impossible liquidation of broken account

## Summary
Severity: High
Contest weight: 0.0168
Dataset id: 8467
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an accounting inconsistency that arises when a token transfer, intended to be used as collateral, reverts. In the CreditManager contract the total collateral value (tv) and the weighted total value (tvw) are updated unconditionally, even if the underlying ERC20 transfer fails. As a result the protocol believes the account holds a certain amount of the token, while the token balance is actually zero. When a liquidator attempts to liquidate the position, the protocol still charges the liquidation fee for the missing token and expects to receive the token, but the transfer cannot be completed. This creates a situation where an under‑collateralised account appears to be sufficiently collateralised on‑chain, making liquidation impossible or causing the liquidator to lose the fee. The impact is that funds can become stuck, risk parameters are violated, and a malicious borrower could deliberately trigger a revert (for example by using a token that reverts on transfer) to protect an unhealthy position. The bug occurs during any operation that updates collateral accounting – typically when adding collateral or during the liquidation routine – and only manifests when the transfer call returns false or throws. It was discovered by the MixBytes audit team while reviewing the lines that accumulate tv and tvw in CreditManager.sol; the logic does not check the transfer result before adjusting the accounting variables, which makes the problem easy to miss because the UI shows the expected collateral value and no error is emitted. To remediate, the contract should only increase tv and tvw after a successful transfer, or revert the accounting changes if the transfer fails, and it must also skip charging the liquidation fee for tokens that were not actually transferred. In broader terms this is a classic “failed transfer accounting” bug, a subclass of improper state updates that break the invariant that recorded collateral matches on‑chain balances, leading to broken liquidation logic and potential loss of funds.

## Recommendation
We recommend not to accumulate tv and tvw in case transfer was reverted.
