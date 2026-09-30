# [H] Withdrawing from the vault may lead to a loss if the order balances are less than the total amount withdrawn

## Summary
Severity: High
Reporter: Nyksx
Contest weight: 0.9547
Dataset id: 4981
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the user withdraws, the withdrawAssets function calls the _burnFromOrder()
if the order is not mature yet.
```solidity
else if (block.timestamp < orderInfo.maturity) {
    // withraw ft and xt from order to burn
    uint256 maxWithdraw = orderInfo.xt.balanceOf(order).min(orderInfo.ft.balanceOf(order));
    if (maxWithdraw < amountLeft) {
        amountLeft -= maxWithdraw;
        _burnFromOrder(ITermMaxOrder(order), orderInfo, maxWithdraw);
        //@audit-issue it burns from the order but didnt transfer
        ++i;
    } else {
        _burnFromOrder(ITermMaxOrder(order), orderInfo, amountLeft);
        asset.safeTransfer(recipient, amountLeft);
        amountLeft = 0;
        break;
    }
} else {
    // ignore orders that are in liquidation window
    ++i;
}
```
The function can only burn an amount equal to the minimum balance of the XT or FT token that the order has. If the withdrawal amount exceeds the maximum burnable amount, the function updates the amountLeft, burns the necessary amount from the current order, and then moves on to the next order to fulfill the withdrawal.
The problem is that the function updates the amountLeft but does not transfer the maxWithdraw amount of tokens to the user after burning from the order. When it moves on to the next order, it only transfers amountLeft - maxWithdraw to the user.

Impact Explanation:
If the balance of orders XT or FT is less than the user's withdrawal amount, the user will incur a loss of funds.

## Proof of Concept
```solidity
function testRedeemWhenTheXtBalanceLessThanWithdrawalAmount() public {
    vm.warp(currentTime + 3 days);
    address lper2 = vm.randomAddress();
    uint256 amount2 = 10000e8;
    res.debt.mint(lper2, amount2);
    vm.startPrank(lper2);
    res.debt.approve(address(vault), amount2);
    uint256 shares = vault.deposit(amount2, lper2);
    vm.stopPrank();
    vm.startPrank(curator);
    address order2 = address(vault.createOrder(market2, maxCapacity, 0, orderConfig.curveCuts));
    uint256[] memory indexes = new uint256[](2);
    indexes[0] = 1;
    indexes[1] = 0;
    vault.updateSupplyQueue(indexes);
    res.debt.mint(curator, 10000e8);
    res.debt.approve(address(vault), 10000e8);
    vault.deposit(10000e8, curator);
    vm.stopPrank();
    vm.warp(currentTime + 4 days);
    // Buy some XT so the XT balance will be less than the withdrawal amount
    {
        address taker = vm.randomAddress();
        uint128 tokenAmtIn = 1000e8;
        res.debt.mint(taker, tokenAmtIn);
        vm.startPrank(taker);
        res.debt.approve(address(res.order), tokenAmtIn);
        res.order.swapExactTokenToToken(res.debt, res.xt, taker, tokenAmtIn, 12000e8);
        vm.stopPrank();
    }
    // User withdraws
    vm.startPrank(lper2);
    uint256 userDebtTokenBalaceBefore = res.debt.balanceOf(lper2);
    console.log("users shares before", vault.balanceOf(lper2));
    console.log("user debt token balance before", userDebtTokenBalaceBefore);
    vault.redeem(shares, lper2, lper2);
    uint256 userDebtTokenBalaceAfter = res.debt.balanceOf(lper2);
    console.log("users shares after", vault.balanceOf(lper2));
    console.log("user debt token balance after", userDebtTokenBalaceAfter);
    vm.stopPrank();
}
```
Even if the user burns 1e12 shares, they will receive only 1e11 debt tokens in return:
Logs:
users shares before 1000000000000
user debt token balance before 0
users shares after 0
user debt token balance after 100000000000

## Recommendation
```solidity
if (maxWithdraw < amountLeft) {
    amountLeft -= maxWithdraw;
    _burnFromOrder(ITermMaxOrder(order), orderInfo, maxWithdraw);
    asset.safeTransfer(recipient, maxWithdraw);
    ++i;
} else {
    _burnFromOrder(ITermMaxOrder(order), orderInfo, amountLeft);
    asset.safeTransfer(recipient, amountLeft);
    amountLeft = 0;
    break;
}
```
