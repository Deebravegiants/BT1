# [M] Reenterable Withdrawal Pattern

## Summary
Severity: Medium
Contest weight: 0.2547
Dataset id: 14703
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The withdrawal of funds from the Account contract is vulnerable to reentrancy.
function withdraw(uint256 amount, address market) external override {
    ITracer _tracer = ITracer(market);
    require(amount > 0, "ACT: Withdraw Amount");
    Types.AccountBalance storage userBalance = balances[market][msg.sender];
    require(
        marginIsValid(
            userBalance.base.sub(amount.toInt256()),
            userBalance.quote,
            pricing.fairPrices(market),
            userBalance.lastUpdatedGasPrice,
            market
        ),
        "ACT: Withdraw below valid Margin"
    );
    address tracerBaseToken = _tracer.tracerBaseToken();
    IERC20(tracerBaseToken).safeTransfer(msg.sender, amount);
    userBalance.base = userBalance.base.sub(amount.toInt256());
    userBalance.deposited = userBalance.deposited.sub(amount);
    int256 originalLeverage = userBalance.totalLeveragedValue;
    _updateAccountLeverage(userBalance.quote, pricing.fairPrices(market), userBalance.base, msg.sender, market, originalLeverage);
    // Safemath will throw if tvl[market] < amount
    tvl[market] = tvl[market].sub(amount);
    emit Withdraw(msg.sender, amount, market);
}
The above code is an excerpt of the function withdraw().
Here the check to ensure that the margin is valid (marginIsValid()) occurs before the funds are transferred to the user in IERC20(tracerBaseToken).safeTransfer(msg.sender, amount), which occurs before the balances are updated.
If a malicious user was able to gain control over the execution during IERC20(tracerBaseToken).safeTransfer(msg.sender, amount) then the user would be able to call withdraw() a second time.
This second call to withdraw() would occur before the users balances have been updated during the first iteration and so they will again pass the check isMarginValid(), even if the margin after both transfers would not be positive.
Thus, the call IERC20(tracerBaseToken).safeTransfer(msg.sender, amount) will be made again.
The user could then take control of the execution and call withdraw() a third time and then a fourth and so on until they have drained their entire userBalance.deposited after which there would be a subtraction underflow preventing further recursions.
Note that the likelihood of this vulnerability is low as the majority of ERC20 tokens do not render control of execution to arbitrary addresses during a call to transfer().

## Recommendation
To prevent reentrancy it is recommended to first perform all state updates before making any external calls to contracts which may be outside the protocols control.
That is the line IERC20(tracerBaseToken).safeTransfer(msg.sender, amount) should occur after all state modifications.
See TCR-27 for further details.
Tracer Protocol
