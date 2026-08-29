# [M] Slippage on `MetapoolRouter.addLiquidityOneETHKeepYt`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-05-napier-update
Published: 2024-05-20
Source: https://github.com/sherlock-audit/2024-05-napier-update-judging/issues/28
Type: sherlock-finding

## Details
Ironsidesec

medium

# Slippage on `MetapoolRouter.addLiquidityOneETHKeepYt`

## Summary
As a user, I don't want to mint liquidity at a lower LP price and receive the manipulated / hugely changed YT price/amount.

A user can call `MetapoolRouter.addLiquidityOneETHKeepYt` to add liquidity (only PT) to metaPool (PT -tricrypto) and get YT (yield tokens)
There's slippage protection `minLiquidity`, but no `minYT`.
Due to volatility or MEV or normal events listed below, the amount of YT tokens received can be fewer which were issued at inflated price which dips within few blocks or receive huge at dipped price because there is no slippage to amount of YT you get.

## Vulnerability Detail

1. Issue PT and YT using the received ETH
2. Add liquidity to the Curve metapool
3. Send the received LP token and YT to the recipient

**Attack / issue flow** :
1. The amount of liquidity to mint depends on the `3LST-PT TriCrypto LP token`, `Napier Principal Token`, and the global scales when issuing the PT + YT tokens.
2. So, if someone removed PT from twocrypto ,then adding even fewer PT tokens than normal will mint more liquidity. So, if the global scales or tranche issues changes, the value of PT decreases, so someone removes PT tokens from two crytpo LP, and since price of PT decreases, makes the amount of YT increase.
3. The exact opposite scenario can happen, where fewer YT tokes are issued but minimum liquidity slippage is passed. So, as a user I don't want to receive lower YT tokens when price of PT/YT suddenly changed. Add slippage to amount of PY issued.

During the issuance, the user will deposit underlying assets (e.g., ETH) to the Tranche contract, and the Tranche contract will forward them to the Adaptor contract for depositing. The number of shares minted is depending on the current scale of the adaptor. The current scale of the adaptor can increase or decrease at any time, depending on the current on-chain condition when the transaction is executed. For instance, the LIDO's daily oracle/rebase update will increase the stETH balance, which will, in turn, increase the adaptor's scale. On the other hand, if there is a mass validator slashing event, the ETH claimed from the withdrawal queue will be less than expected, leading to a decrease in the adaptor's scale. Thus, one cannot ensure the result from the off-chain simulation will be the same as the on-chain execution.

https://github.com/sherlock-audit/2024-05-napier-update/blob/c31af59c6399182fd04b40530d79d98632d2bfa7/metapool-router/src/MetapoolRouter.sol#L356-L392

```solidity
File: 2024-05-napier-update\metapool-router\src\MetapoolRouter.sol

371:     function addLiquidityOneETHKeepYt(address metapool, uint256 minLiquidity, address recipient, uint256 deadline)
372:         external payable nonReentrant checkDeadline(deadline) checkMetapool(metapool) returns (uint256 liquidity)
378:     {
379:         // Steps:
380:         // 1. Issue PT and YT using the received ETH
381:         // 2. Add liquidity to the Curve metapool
382:         // 3. Send the received LP token and YT to the recipient
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2024-05-napier-update-judging/issues/28_
