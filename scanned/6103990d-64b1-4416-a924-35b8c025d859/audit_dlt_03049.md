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



_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1430_
