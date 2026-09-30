# [H] updateState() should be called in depositEth()

## Summary
Severity: High
Contest weight: 0.6358
Dataset id: 17603
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Whenever the liquidity of a LToken changes, getRateFactor will be changed.
Therefore, updateState() must be called prior to the change to settle the pending interests.
Alice is a liquidity provider for LEther, Bob is a borrower.
1. Alice added 1000 ETH;
2. Bob borrowed 500 ETH; In which updateState() is called. The util in getBorrowRatePerSecond is 0.5 now.
3. One year later (no one interacts with the asset for 1 year), Alice redeemed 500 ETH with redeemEth(), in which updateState() is not called. The util in getBorrowRatePerSecond is 1 now.
4. Bob called repay(), in which updateState() is called to calculates the pending interest:
For Bob the borrower, the sum of principal and interest is:
BorrowRatePerSecond = c3×(util ×c1+util32 ×c1+util64 ×c2)/secsPerYear = 5545529241
rateFactor = BorrowRatePerSecond × secsPerYear / 1e18 = 175000000081490720
sum = borrow × rateFactor / 1e18 + borrow = 587
But the actual sum is as below, due to updateState() is not called in redeemEth():
BorrowRatePerSecond = c3×(util×c1+util32×c1+util64×c2)/secsPerYear = 55455292386
rateFactor = BorrowRatePerSecond × secsPerYear / 1e18 = 1750000000000000000
sum = borrow × rateFactor / 1e18 + borrow = 1375
As a result, Bob the borrower is now paying 1375 instead of 587 for the interest, which is 2x the expected amount.
On the other hand, if another liquidity provider called depositEth() before Bob repays the loan, the actual interest can be lower than expected, which constitutes a loss of yields to Alice.
Incorrect amounts of interests will be paid by the borrowers, which can result in loss of yields to the lenders or overpaid interest for the borrowers.

## Recommendation
beforeDeposit() should be called in depositEth() and redeemEth():
```solidity
/**
Transfers shares to the user denoting the amount of Eth deposited
*/
function depositEth() external payable {
    uint assets = msg.value;
    uint shares = previewDeposit(assets);
    require(shares != 0, "ZERO_SHARES");
    beforeDeposit(assets, shares);
    IWETH(address(asset)).deposit{value: assets}();
    _mint(msg.sender, shares);
    emit Deposit(msg.sender, msg.sender, assets, shares);
}

/**
Amount of Eth transferred will be the total underlying assets that are represented by the shares
*/
function redeemEth(uint shares) external {
    uint assets = previewRedeem(shares);
    beforeWithdraw(assets, shares);
    _burn(msg.sender, shares);
    emit Withdraw(msg.sender, msg.sender, msg.sender, assets, shares);
    IWETH(address(asset)).withdraw(assets);
    msg.sender.safeTransferEth(assets);
}
```
Confirmed fix.
