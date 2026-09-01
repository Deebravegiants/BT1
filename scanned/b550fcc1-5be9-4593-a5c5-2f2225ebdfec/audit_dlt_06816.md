# [M] Interface improperly implemented

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-01-dev-test-repo
Published: 2023-12-12
Source: https://github.com/code-423n4/2022-01-dev-test-repo-findings/issues/233
Type: code-finding

## Details
### Lines of code

--------------

[34](https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/Swapper/UniswapV3Swapper.sol#L34-L34), [34](https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/Swapper/UniswapV3Swapper.sol#L34-L34), [34](https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/Swapper/UniswapV3Swapper.sol#L34-L34), [34](https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/Swapper/UniswapV3Swapper.sol#L34-L34), [30](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/glp/GlpStrategy.sol#L30-L30), [31](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/glp/GlpStrategy.sol#L31-L31), [32](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/glp/GlpStrategy.sol#L32-L32), [34](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/glp/GlpStrategy.sol#L34-L34), [35](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/glp/GlpStrategy.sol#L35-L35), [38](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/glp/GlpStrategy.sol#L38-L38), [39](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/glp/GlpStrategy.sol#L39-L39), [40](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/glp/GlpStrategy.sol#L40-L40), [41](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/glp/GlpStrategy.sol#L41-L41)

### Vulnerability details

-------------

The variables below have the same name as an interface function. Because the contract does not extend the interface, the compiler was unable to catch the fact that the variable is not `public` or `external`, and therefore all external references to the interface's function will revert. Change the visibility of the variables to `public`

```solidity
File: contracts/Swapper/UniswapV3Swapper.sol

/// @audit ITapiocaOptionLiquidityProvision.yieldBox()
/// @audit IPenrose.yieldBox()
/// @audit IStrategy.yieldBox()
/// @audit IMarket.yieldBox()
34:      IYieldBox private immutable yieldBox;

```



```solidity
File: contracts/glp/GlpStrategy.sol

/// @audit IGmxRewardRouterV2.gmx()
30:      IERC20 private immutable gmx;

/// @audit IGmxRewardRouterV2.esGmx()
31:      IERC20 private immutable esGmx;

/// @audit IGmxRewardRouterV2.weth()
32:      IERC20 private immutable weth;

/// @audit IGmxRewardRouterV2.feeGmxTracker()
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-01-dev-test-repo-findings/issues/233_
