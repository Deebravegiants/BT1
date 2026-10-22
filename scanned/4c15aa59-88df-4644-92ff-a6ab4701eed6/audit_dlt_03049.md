# [M] LidEthStrategys Hardcoded 2.5% slippage allows stealing all tokens above $2MLN

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1430
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/lido/LidoEthStrategy.sol#L149-L157


# Vulnerability details


### Impact
The `LidEthStrategy` uses a hardcoded 2.5% Slippage for `_withdraw`

https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/lido/LidoEthStrategy.sol#L149-L157

```solidity
        if (amount > queued) {
            uint256 toWithdraw = amount - queued; //1:1 between eth<>stEth
            uint256 minAmount = toWithdraw - (toWithdraw * 250) / 10_000; //2.5%
            uint256 obtainedEth = curveStEthPool.exchange(
                1,
                0,
                toWithdraw,
                minAmount
            );

            INative(address(wrappedNative)).deposit{value: obtainedEth}();
```

2.5% is a VERY high slippage for Curve StableSwaps

On Mainnet, you'd need to swap over 140k ETH to trigger such a change

However, the Swap Fee for this pair is 1BPS

Meaning it's EXTREMELY cheap to manipulate the price to cause it to have a 2.5% Loss

This means that for most withdrawals, the strategy is leaking 2.5% of value (2 BPS + Gas is negligible in this context)


### POC

We need to sell 135k stETH to move the price by 2.5% (due to Curve being really efficient)

```
|Sell up to |Fees       |Minimum Strategy Size|In USD     |Fee   |USD PRICE|
|-----------|-----------|---------------------|-----------|------|---------|
|134880.7225|26.97614449|1079.04578           |1996234.693|0.0002|1850     |
```


This costs us 13.5 ETH

I have doubled it to simulate a backrun as well

27 ETH / 0.025 % = 1080 ETH

As you can see, this means that if the Strategy has more than around $2MLN in value, it will leak more than the fees, allowing the attacker to repeatedly sandwhich it to profit

Notice that because of this, all of the tokens can be stolen, this is not merely "MEV"ing the deposit and withdrawals, this will actually cause a total loss until the Strategy Leaked Amounts will no longer be worth the cost of manipulation (26 ETH per pass)


### POC Steps

- Imbalance Pool to have a discount
- Deposit
- Imbalance Pool to make it lose 2.5%
- Trigger Withdrawal
- Repeat until TVL of strategy is below the profitable threshold (1080 ETH)

### Mitigation Step

I believe the only solution here is to avoid single sided exposure, denominate the strategy either in the LP token or in stETH

Do not swap the tokens back to ETH which is the root of the issue since the exchange rate is manipulatable in multiple ways as demonstrated above


### Additional Resources

The amount of swaps to trigger the slippage are obtained via this library I wrote:

(Results brute forced via: https://github.com/GalloDaSballo/pool-math)



## Assessed type

ERC4626
