# [M] Anyone can manipulate the AL ratio.

## Summary
Severity: Medium
Chain: Smart contract
Component: Origami
Published: 2024-02-27
Source: https://github.com/hats-finance/Origami-0x998f1b716a5022be026ca6b919c0ddf45ca31abd/issues/41
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x645ef5fe0b6086692dd399b8a675ea85fef135ed5a8329bac13054d8b46fdab0
**Severity:** medium

**Description:**
**Description**\
For the `LovDSR` vault, maintaining the `A/L`  ratio within the `target range` is crucial to maintain the desired exposure. 
Various operations are tied to this `ratio`, and any action that pushes it outside the defined range is reversed. 
Thus, ensuring the `ratio` remains within the `valid range` is most important.
However, there is a risk of manipulation by any user, potentially causing the protocol to freeze. 
While such malicious activity could result in the loss of funds for the malicious users, there may be scenarios where they can recover most of their funds.


**Attack Scenario**\
Imagine that the `LovDSR` vault currently holds `3000` `sDAI`, with `300` `sDAI` contributed by users and `2700` `sDAI` obtained through borrowing `USDC`.
The `300 sDAI` includes a deposit of `200 sDAI` from `User A`.

`User A` repays `900 USDC` to the `LovDSR` vault and this is possible due to the absence of access checking.
```
function repay(uint256 amount, address borrower) external override returns (uint256 amountRepaid) {
@1:     uint256 _debtBalance = debtToken.balanceOf(borrower);     // 18 dp
@2:     uint256 _maxRepayAmount = _debtBalance.scaleDown(_assetScalar, OrigamiMath.Rounding.ROUND_UP);   // asset's dp

    uint256 _debtToTransfer;  // 18 dp
    if (amount < _maxRepayAmount) {
@3:       amountRepaid = amount;
@4:        _debtToTransfer = amount.scaleUp(_assetScalar);
    } else {
        amountRepaid = _maxRepayAmount;
        _debtToTransfer = _debtBalance;
    }

    if (amountRepaid != 0) {
@5:     _repay(msg.sender, borrower, _borrowerConfig, amountRepaid, _debtToTransfer);
    }
}
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Origami-0x998f1b716a5022be026ca6b919c0ddf45ca31abd/issues/41_
