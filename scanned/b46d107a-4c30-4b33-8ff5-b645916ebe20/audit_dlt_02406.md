# [?] Conic_exp2 exploit (2023-07)

## Summary
Severity: Unknown
Chain: Ethereum
Component: Conic_exp2
Published: 2023-07
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-07/Conic_exp2.sol
Type: defi-exploit-poc

## Details
References:
- https://twitter.com/BlockSecTeam/status/1682346827939717120

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

// @KeyInfo - Total Lost : ~3M USD$
// Attacker : https://etherscan.io/address/0x8d67db0b205e32a5dd96145f022fa18aae7dc8aa
// Attack Contract : https://etherscan.io/address/0x743599ba5cfa3ce8c59691af5ef279aaafa2e4eb
// Vulnerable Contract : https://etherscan.io/address/0xbb787d6243a8d450659e09ea6fd82f1c859691e9
// Attack Tx : https://etherscan.io/tx/0x8b74995d1d61d3d7547575649136b8765acb22882960f0636941c44ec7bbe146

// @Analysis
// https://twitter.com/BlockSecTeam/status/1682346827939717120

interface IConic {
    function deposit(uint256 underlyingAmount, uint256 minLpReceived, bool stake) external returns (uint256);

    function handleDepeggedCurvePool(
        address curvePool_
    ) external;

    function withdraw(uint256 conicLpAmount, uint256 minUnderlyingReceived) external returns (uint256);
}

contract ConicFinanceTest is Test {
    IWETH WETH = IWETH(payable(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2));
    IERC20 rETH = IERC20(0xae78736Cd615f374D3085123A210448E74Fc6393);
    IERC20 stETH = IERC20(0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84);
    IERC20 cbETH = IERC20(0xBe9895146f7AF43049ca1c1AE358B0541Ea49704);
    IERC20 steCRV = IERC20(0x06325440D014e39736583c165C2963BA99fAf14E);
    IERC20 cbETH_ETHf = IERC20(0x5b6C539b224014A09B3388e51CaAA8e354c959C8);
    IERC20 rETH_ETHf = IERC20(0x6c38cE8984a890F5e46e6dF6117C26b3F1EcfC9C);
    IERC20 cncETH = IERC20(0x3565A68666FD3A6361F06f84637E805b727b4A47);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-07/Conic_exp2.sol_
