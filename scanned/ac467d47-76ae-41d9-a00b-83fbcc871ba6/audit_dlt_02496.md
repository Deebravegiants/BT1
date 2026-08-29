# [?] LinkDAO - Bad `K` Value Verification

## Summary
Severity: Unknown
Chain: BNB Chain
Component: LinkDao
Published: 2023-11-15
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-11/LinkDao_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$30K

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "forge-std/Test.sol";

// @KeyInfo - Total Lost : ~$30K
// Attacker : https://bscscan.com/address/0xdf6b0200b4e1bc4a310f33df95a9087cc2c79038
// Attack Contract : https://bscscan.com/address/0x721a66c7767103e7dcacf8440e8dd074edff40a8
// Vulnerable Contract : https://bscscan.com/address/0x6524a5fd3fec179db3b3c1d21f700da7abe6b0de
// Attack Tx : https://explorer.phalcon.xyz/tx/bsc/0x4ed59e3013215c272536775a966f4365112997a6eec534d38325be014f2e15ee

// @Info
// Vulnerable Contract Code : https://bscscan.com/address/0x6524a5fd3fec179db3b3c1d21f700da7abe6b0de#code

// @Analysis
// Twitter Guy : https://x.com/phalcon_xyz/status/1725058908144746992

interface IUniswapV2Pair {
    event Transfer(address indexed from, address indexed to, uint256 value);

    function balanceOf(
        address owner
    ) external view returns (uint256);
    function transfer(address to, uint256 value) external returns (bool);

    event Swap(
        address indexed sender,
        uint256 amount0In,
        uint256 amount1In,
        uint256 amount0Out,
        uint256 amount1Out,
        address indexed to
    );

    function swap(uint256 amount0Out, uint256 amount1Out, address to, bytes calldata data) external;
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-11/LinkDao_exp.sol_
