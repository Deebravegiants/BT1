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
@1: `debtBalance = 2700 * 1e18`
@2:  `_maxRepayAmount  = 2700 * 1e6`
@3: `amountRepaid  = 900 * 1e6`
@4: `_debtToTransfer  = 900 * 1e18`
@5: `_repay` function is invoked.

```
function _repay(address from,  address borrower,  BorrowerConfig storage borrowerConfig, uint256 repayAmount, uint256 debtToTransfer) private {
@6:    debtToken.safeTransferFrom(borrower, address(idleStrategyManager), debtToTransfer);
}
```
@6: we burn the debt `900 USDC` from `LovDSR` vault.

Another `borrower` borrows this amount, or `oUSDC` investors exit their investment, thereby preventing the `LovDSR` vault from borrowing `USDC    ` in the future.

The `A/L` ratio shifts from `10/9` to `10/6 (= 3000 / 1800)`,

Now any investment in the `LovDSR` will be reverted.
```
function investWithToken(
    address account,
    IOrigamiInvestment.InvestQuoteData calldata quoteData
) external virtual override onlyLovToken returns (
    uint256 investmentAmount
) {
    if (cache.liabilities != 0) {
        cache.assets = reservesBalance();
        cache.liabilities = liabilities(IOrigamiOracle.PriceType.SPOT_PRICE);
        uint128 newAL = _assetToLiabilityRatio(cache);
@7:        _validateALRatio(userALRange, oldAL, newAL, AlValidationMode.HIGHER_THAN_BEFORE);
    }
}
```
@7: revert here

The same applies to exiting investments
```
function exitToToken(
    address /*account*/,
    IOrigamiInvestment.ExitQuoteData calldata quoteData,
    address recipient
) external virtual override onlyLovToken returns (
    uint256 toTokenAmount,
    uint256 toBurnAmount
) {
    if (cache.liabilities != 0) {
        cache.assets = reservesBalance();
    cache.liabilities = liabilities(IOrigamiOracle.PriceType.SPOT_PRICE);
        uint128 newAL = _assetToLiabilityRatio(cache);
@8:        _validateALRatio(userALRange, oldAL, newAL, AlValidationMode.LOWER_THAN_BEFORE);
    }
}
```
@8: revert here

The `rebalanceDown` function cannot help because the `LovDSR` vault is unable to borrow `USDC` because there is no available `USDC`.

To interact with the `LovDSR`, one potential solution is to repay the outstanding debt. 
This could involve using new `USDC` or utilizing `reserves` from the `LovDSR` vault. 
With the `LovDSR` still holding `3000 sDAI`, converting `1800 sDAI` to `1800 USDC` for repayment would leave `1200 sDAI` remaining. 
In this scenario, `User A` could retain `800 sDAI (1200 * 2 / 3)`, resulting in a loss of `300 sDAI`.

Of course, this example serves to illustrate one potential solution. 
In reality, encountering such a malicious user might be unlikely, but it's important to consider and mitigate any potential risks.

**Attachments**
    
    1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
Restrict repayment of debt to borrowers only.
Or restrict repayment to elevated users only.
