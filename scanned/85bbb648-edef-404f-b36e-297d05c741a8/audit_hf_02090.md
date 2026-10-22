# [H] Forced Investment Risk in BalancerUpgradeable and VelodromPoolAdapter

## Summary
Severity: High
Contest weight: 0.6362
Dataset id: 11793
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Cadabra protocol is a yield-farming protocol with a number of strategies that aim to guarantee continuity of passive yield. While examining current investment logic, we notice a potential force investment risk that has been exploited in earlier hacks, e.g., yDAI [13] and BT.Finance [1]. To elaborate, we show below the related BaseAdapter::_investInternal() routine. Specifially, the BalancerUpgradeable contract is designed and implemented to invest user funds, harvest growing yields, and return any gains, if any, to the users. In addition, the investment logic interacts with underlying strategies via associated adapters. To elaborate, we show below the implementation of the affected VelodromePoolAdapter::_invest() routine.
```solidity
function _investInternal(address dustReceiver) internal returns (uint256 valueBefore, uint256 valueAfter) {
    (valueBefore,) = value();
    _invest();
    (valueAfter,) = value();
    _returnDust(dustReceiver);
}

function _invest() internal override {
    uint deposit0;
    uint deposit1;
    // the tokens we have on our balance. We need to deposit them in accordance to the pair's ratio
    uint balance0 = TOKEN0.balanceOf(address(this));
    uint balance1 = TOKEN1.balanceOf(address(this));
    (uint reserve0, uint reserve1,) = POOL.getReserves();
    if (reserve0 == 0 || reserve1 == 0) {
        revert ZeroReserveBalance(reserve0, reserve1);
    }
    deposit0 = balance0;
    deposit1 = deposit0 * reserve1 / reserve0;
    if (deposit1 > balance1) {
        deposit1 = balance1;
        deposit0 = deposit1 * reserve0 / reserve1;
    }
    TOKEN0.safeTransfer(address(POOL), deposit0);
    TOKEN1.safeTransfer(address(POOL), deposit1);
    POOL.mint(address(this));
    GAUGE.deposit(POOL.balanceOf(address(this)));
}
```
It comes to our attention that the above investment logic does not perform any health check: it does not have the stability check on the liquidity pool into which the user funds will be added. In other words, if the configured strategy blindly invests the deposited funds into an imbalanced Velodrome pool, the strategy will not result in a profitable investment. In fact, earlier incidents (yDAI and BT.Finance hacks [1, 13]) have prompted the need of a guarded call before kicking off the actual investment. For the very same reason, we argue for the guarded stability check associated with every single _invest() call. In the meantime, it is important to highlight that the current approach to evaluate the total value managed by the protocol is not reliable. Specifically, it suffers from a sandwich-based attack in arbitrarily inflate or deflate the value at will.

## Recommendation
Ensure the target liquidity pool is stable before the user funds can be added into as liquidity.
