# [M] Accounts will not be liquidated when they

## Summary
Severity: Medium
Contest weight: 0.4616
Dataset id: 20070
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the case that the totalMaintenance * liquidationFee is higher than the account's totalCollateral, liquidators are paid the totalCollateral. I think one of the reasons for this is to avoid the case where liquidating an account would attempt to debit fees that is greater than the collateral balance. The problem is that, the value of totalCollateral used as fee is slightly higher value than the current collateral balance, which means that in such cases, attempts to liquidate the account would revert due to underflow errors.

Here is the liquidate function:
```solidity
function liquidate(
    address account,
    IProduct product
) external nonReentrant notPaused isProduct(product)
settleForAccount(account, product) {
    if (product.isLiquidating(account)) revert CollateralAccountLiquidatingError(account);
    if (!totalMaintenance.gt(totalCollateral))
        revert CollateralCantLiquidate(totalMaintenance, totalCollateral);
    product.closeAll(account);
    // claim fee
    collateralForFee.mul(liquidationFee));
    _products[product].debitAccount(account, fee);
    token.push(msg.sender, fee);
    emit Liquidation(account, product, msg.sender, fee);
}
```
fee = min(totalCollateral, collateralForFee * liquidationFee). But the PROBLEM is, the value of totalCollateral is fetched before calling product.closeAll, and product.closeAll debits the closePosition fee from the collateral balance. So there is an attempt to debit totalCollateral, when the current collateral balance of the account is totalCollateral - closePositionFees. This allows the following:
• There is an ETH-long market with following configs:
– maintenance = 5%
– minCollateral = 100 USDC
– liquidationFee = 20%
– ETH price = $1000
• User uses 500 USDC to open $10000 (10 ETH) position
• Price of ETH spikes up to $6000
• Required maintenance = 60000 * 5% = $3000 which is higher than account's collateral balance (500 USDC), therefore account should be liquidated
• A watcher attempts to liquidate the account which does the following:
– totalCollateral = 500 USDC
– product.closeAll closes the position and debits a makerFee of 10 USDC
– current collateral balance = 490 USDC
– collateralForFee = totalMaintenance = $3000
– fee = min(500, 3000 * 20%) = 500
– _products[product].debitAccount(account, fee) attempts to subtract 500 from 490 which would revert due to underflow
– account does not get liquidated
• Now, User is not liquidated even when he is using 500 USD to control a $60000 position at 120x leverage (whereas, maxLeverage = 20x)
(1/liquidationFee)x. In the above example, price of ETH increased by 6x (from 1000 USD to 6000 USD) which is greater than 5 (1/20%)

A User's position will not be liquidated even when his collateral balance falls WELL below the required maintenance. I believe this is of HIGH impact because this scenario is very likely to happen, and when it does, the protocol will be greatly affected because a lot of users will be trading abnormally high leveraged positions without getting liquidated.

## Recommendation
totalCollateral that would be paid to liquidator should be refetched after product.closeAll is called to get the current collateral balance after closePositionFees have been debited.
