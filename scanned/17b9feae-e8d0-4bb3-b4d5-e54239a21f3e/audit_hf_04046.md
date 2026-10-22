# [H] No slippage protection when withdrawing and

## Summary
Severity: High
Contest weight: 0.5781
Dataset id: 20485
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When rebalanceAll is called, the liquidity is first withdrawn from the pools and then deposited to new positions. However, there is no slippage protection for these operations. In the rebalanceAll function, it first withdraws all liquidity from the pools and deposits all liquidity to new positions. ```solidity _withdraw(_totalSupply, _totalSupply); ntracts/Multipool.sol#L853-L853 _deposit(reserve0, reserve1, _totalSupply, slots); ntracts/Multipool.sol#L885-L885 ``` However, there are no parameters for amount0Min and amount1Min, which are used to prevent slippage. These parameters should be checked to create slippage protections. https://docs.uniswap.org/contracts/v3/guides/providing-liquidity/decrease-liquidity https://docs.uniswap.org/contracts/v3/guides/providing-liquidity/increase-liquidity in the rebalanceAll function. wagmi/blob/main/concentrator/contracts/Multipool.sol#L559-L560 The withdraw and provide liquidity operations in rebalanceAll are exposed to high slippage and could result in a loss for LPs of multipool.

## Recommendation
Implement slippage protection in rebalanceAll as suggested to avoid loss to the protocol.
