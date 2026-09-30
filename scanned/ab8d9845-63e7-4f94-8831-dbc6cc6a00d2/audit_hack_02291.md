# [M] \[M03\] Undocumented decimal assumptions

## Summary
Severity: Medium
Source: https://github.com/1inch/limit-order-protocol/blob/4d94eea25e4dac6271bfd703096a5c4a4d899b4a/contracts/LimitOrderProtocol.sol
Type: audit-issue

## Details
The [LimitOrderProtocol](https://github.com/1inch/limit-order-protocol/blob/4d94eea25e4dac6271bfd703096a5c4a4d899b4a/contracts/LimitOrderProtocol.sol) contract inherits the [ChainlinkCalculator](https://github.com/1inch/limit-order-protocol/blob/4d94eea25e4dac6271bfd703096a5c4a4d899b4a/contracts/helpers/ChainlinkCalculator.sol) contract through the [OrderMixin](https://github.com/1inch/limit-order-protocol/blob/4d94eea25e4dac6271bfd703096a5c4a4d899b4a/contracts/OrderMixin.sol) contract. This contract exposes two functions to enable the usage of Chainlink oracles during the [predicates check](https://github.com/1inch/limit-order-protocol/blob/4d94eea25e4dac6271bfd703096a5c4a4d899b4a/contracts/OrderMixin.sol#L218) and the lookup of the [maker amount](https://github.com/1inch/limit-order-protocol/blob/4d94eea25e4dac6271bfd703096a5c4a4d899b4a/contracts/OrderMixin.sol#L315)/[taker amount](https://github.com/1inch/limit-order-protocol/blob/4d94eea25e4dac6271bfd703096a5c4a4d899b4a/contracts/OrderMixin.sol#L326).

However, the contract makes undocumented assumptions about the number of decimals that the Chainlink oracles should report in, as well as the number of decimals that the function parameters should contain. In certain scenarios, this could lead to unexpected behaviors, including the mis-pricing of assets and the unintentional loss of funds.

More specifically, throughout the contract the implicit assumption is that the Chainlink oracles will report with 18 decimals of precision. However, not [all Chainlink oracles](https://docs.chain.link/docs/ethereum-addresses/) report with this number of decimals. In fact, if the oracle reports a token pair that is in terms of a currency (USD, for instance), it will only have 8 decimals of precision. Since there are no restrictions on _which_ oracles can be used, implicit assumptions should not be made about the number of decimals they will report with.

Relatedly, there is an implicit assumption that the `amount` parameter for the `ChainlinkCalculator` functions will use 18 decimals, together with the misleading explicit declaration that the [singlePrice](https://github.com/1inch/limit-order-protocol/blob/4d94eea25e4dac6271bfd703096a5c4a4d899b4a/contracts/helpers/ChainlinkCalculator.sol#L21) function [Calculates price of token relative to ETH scaled by 1e18](https://github.com/1inch/limit-order-protocol/blob/4d94eea25e4dac6271bfd703096a5c4a4d899b4a/contracts/helpers/ChainlinkCalculator.sol#L14). In reality, even with an oracle that _does_ report with 18 decimals, the return value of the `singlePrice` function would be scaled by the number of decimals of the `amount` parameter, which may not necessarily be 18 decimals.

Similarly, the [doublePrice](https://github.com/1inch/limit-order-protocol/blob/4d94eea25e4dac6271bfd703096a5c4a4d899b4a/contracts/helpers/ChainlinkCalculator.sol#L35) function assumes that two Chainlink oracles will report with the same number of decimals, causing the result of the function to deviate from expectations.

Consider explicitly documenting assumptions regarding the number of decimals that parameters and return values should be in terms of. Furthermore, consider either limiting calculations that depend on oracles that break those assumptions, or having the relevant calculations take the actual number of decimals into account.

_**Update:** Fixed in [pull request #75](https://github.com/1inch/limit-order-protocol/pull/75)._
