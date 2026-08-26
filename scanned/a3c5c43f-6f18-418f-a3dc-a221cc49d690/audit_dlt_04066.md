# [M] Slippage Control `trade.limit` Is Ignored By 0x Adaptor

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-notional
Published: 2022-10-13
Source: https://github.com/sherlock-audit/2022-09-notional-judging/issues/74
Type: sherlock-finding

## Details
xiaoming90

high

# Slippage Control `trade.limit` Is Ignored By 0x Adaptor

## Summary

The slippage control (`trade.limit`) is not parsed and ignored by 0x adaptor when executing a trade. 

## Vulnerability Detail

> Note: This issue only affects the 0x adaptor.  The rest of the in-scope adaptors (Curve, Balancer V2, Uniswap V2, Uniswap V3) adhere to the `trade.limit` setting.

The `trade.limit` parameter exists to ensure that the vault receives a minimum amount of purchased/output tokens during the trade. If the vault received less than the `trade.limit`, the transaction would revert. Refer to the next section for more detail about `trade.limit`. However, the problem is that the `trade.limit` is ignored by the 0x adaptor and not explicitly enforced within the 0x adaptor. This also means that there is no slippage control at all if the trade is executed via 0x DEX since the slippage control is implemented via the use of the `trade.limit` that is ignored by 0x adaptor.

https://github.com/sherlock-audit/2022-09-notional/blob/main/leveraged-vaults/contracts/trading/adapters/ZeroExAdapter.sol#L7

```solidity
File: ZeroExAdapter.sol
07: library ZeroExAdapter {
08:     /// @dev executeTrade validates pre and post trade balances and also
09:     /// sets and revokes all approvals. We are also only calling a trusted
10:     /// zero ex proxy in this case. Therefore no order validation is done
11:     /// to allow for flexibility.
12:     function getExecutionData(address from, Trade calldata trade)
13:         internal view returns (
14:             address spender,
15:             address target,
16:             uint256 /* msgValue */,
17:             bytes memory executionCallData
18:         )
19:     {
20:         spender = Deployments.ZERO_EX;
21:         target = Deployments.ZERO_EX;
22:         // msgValue is always zero
23:         executionCallData = trade.exchangeData;
24:     }
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-09-notional-judging/issues/74_
