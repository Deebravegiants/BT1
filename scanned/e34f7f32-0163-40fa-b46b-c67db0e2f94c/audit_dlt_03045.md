# [M] Oracle is susceptible to manipulation if deployed on Optimism

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1474
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/Swapper/UniswapV3Swapper.sol#L97


# Vulnerability details

## Impact

the cost of manipulating TWAP in Optimism L2 network too low so TWAP oracle should not be used in optimism

## Proof of Concept

The protocol intend to deploy on L2 network

according to

https://docs.tapioca.xyz/tapioca/information/supported-chains

> Arbitrum (Host)
> Optimism
> Ethereum

Arbitrum is the host chain, the optimism and ethereum will be supported as well

The information provided by the Uniswap team, as documented in the [Uniswap Oracle Integration on Layer 2 Rollups guide](https://docs.uniswap.org/concepts/protocol/oracle#oracles-integrations-on-layer-2-rollups), primarily addresses the integration of Uniswap oracle on L2 Optimism. However, it is relevant to note that the same concerns apply to Arbitrum as well. Arbitrum's average block time is approximately 0.25 seconds, making it vulnerable to potential oracle price manipulation.

> Oracles Integrations on Layer 2 Rollups

> Optimism

> On Optimism, every transaction is confirmed as an individual block. The block.timestamp of these blocks, however, reflect the block.timestamp of the last L1 block ingested by the Sequencer. For this reason, Uniswap pools on Optimism are not suitable for providing oracle prices, as this high-latency block.timestamp update process makes the oracle much less costly to manipulate. In the future, it's possible that the Optimism block.timestamp will have much higher granularity (with a small trust assumption in the Sequencer), or that forced inclusion transactions will improve oracle security. For more information on these potential upcoming changes, please see the Optimistic Specs repo. For the time being, usage of the oracle feature on Optimism should be avoided.

but such TWAP oracle is used as a source of oracle to determine the borrow / lending exchange rate and also the option token exercise price

also, the TWAP oracle is used to getOutputAmount in UniswapV3

the code is [here](https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/Swapper/UniswapV3Swapper.sol#L97)

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1474_
