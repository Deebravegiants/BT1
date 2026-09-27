# [M] \[M01\] Cannot unpause exchange

## Summary
Severity: Medium
Source: https://github.com/1inch-exchange/1inch-v2-contracts/blob/72f2812837fdd73ec2d32c8988811df361e80985/contracts/OneInchExchange.sol#L179
Type: audit-issue

## Details
The `OneInchExchange.sol` contract exposes [a mechanism](https://github.com/1inch-exchange/1inch-v2-contracts/blob/72f2812837fdd73ec2d32c8988811df361e80985/contracts/OneInchExchange.sol#L179) for the owner to pause the contract. This [disables the swap functionality](https://github.com/1inch-exchange/1inch-v2-contracts/blob/72f2812837fdd73ec2d32c8988811df361e80985/contracts/OneInchExchange.sol#L99). However, there is no corresponding mechanism to unpause the contract.

Consider introducing a mechanism for the owner to unpause the contract. Alternatively, if the current behavior is expected, consider renaming the `pause` function to `shutdown` or something similar that implies the contract will be permanently disabled.

**Update**: _Fixed in [commit 0b89110a](https://github.com/1inch-exchange/1inch-v2-contracts/commit/0b89110ae5cc73c8b3f4baf8f2c4b8b290b1f923). The `pause` function has been renamed to `shutdown`._
