# [?] HundredFinance - Donate Inflation ExchangeRate && Rounding Error

## Summary
Severity: Unknown
Chain: Optimism
Component: HundredFinance_2
Published: 2023-04-15
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-04/HundredFinance_2_exp.sol
Type: defi-exploit-poc

## Details
Lost: $7M
References:
- https://twitter.com/peckshield/status/1647307128267476992
- https://twitter.com/danielvf/status/1647329491788677121
- https://twitter.com/hexagate_/status/1647334970258608131
- https://optimistic.etherscan.io/tx/0x6e9ebcdebbabda04fa9f2e3bc21ea8b2e4fb4bf4f4670cb8483e2f0b2604f451

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

// @Analysis
// https://twitter.com/peckshield/status/1647307128267476992
// https://twitter.com/danielvf/status/1647329491788677121
// https://twitter.com/hexagate_/status/1647334970258608131
// @TX
// https://optimistic.etherscan.io/tx/0x6e9ebcdebbabda04fa9f2e3bc21ea8b2e4fb4bf4f4670cb8483e2f0b2604f451
// @Summary
// https://blog.hundred.finance/15-04-23-hundred-finance-hack-post-mortem-d895b618cf33

interface IChainlinkPriceOracleProxy {
    function getUnderlyingPrice(
        address cToken
    ) external view returns (uint256);
}

contract contractTest is Test {
    IERC20 WBTC = IERC20(0x68f180fcCe6836688e9084f035309E29Bf0A2095);
    IERC20 USDC = IERC20(0x7F5c764cBc14f9669B88837ca1490cCa17c31607);
    IERC20 SNX = IERC20(0x8700dAec35aF8Ff88c16BdF0418774CB3D7599B4);
    IERC20 sUSD = IERC20(0x8c6f28f2F1A3C87F0f938b96d27520d9751ec8d9);
    IERC20 USDT = IERC20(0x94b008aA00579c1307B0EF2c499aD98a8ce58e58);
    IERC20 DAI = IERC20(0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1);
    ICErc20Delegate hWBTC = ICErc20Delegate(0x35594E4992DFefcB0C20EC487d7af22a30bDec60);
    crETH CEther = crETH(0x1A61A72F5Cf5e857f15ee502210b81f8B3a66263);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-04/HundredFinance_2_exp.sol_
