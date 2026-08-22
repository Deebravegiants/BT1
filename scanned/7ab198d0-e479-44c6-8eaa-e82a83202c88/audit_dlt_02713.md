# [?] Matez - Integer Truncation

## Summary
Severity: Unknown
Chain: BNB Chain
Component: Matez
Published: 2024-11-21
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-11/Matez_exp.sol
Type: defi-exploit-poc

## Details
Lost: 80k USD

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.15;

import "../basetest.sol";

// @KeyInfo - Total Lost : 80k USD
// Attacker : https://bscscan.com/address/0xd4f04374385341da7333b82b230cd223143c4d62
// Attack Contract : https://bscscan.com/address/0x0aD02ce1b8EB978FD8dc4abeC5bf92Dfa81Ed705
// Vulnerable Contract : https://bscscan.com/address/0x326FB70eF9e70f8f4c38CFbfaF39F960A5C252fa
// Attack Tx : https://bscscan.com/tx/0x840b0dc64dbb91e8aba524f67189f639a0bc94ee9256c57d79083bb3fd46ec91

// @Info
// Vulnerable Contract Code : https://bscscan.com/address/0x326FB70eF9e70f8f4c38CFbfaF39F960A5C252fa#code

// @Analysis
// Post-mortem : N/A
// Twitter Guy : https://x.com/TenArmorAlert/status/1859830885966905670
// Hacking God : N/A
pragma solidity ^0.8.0;

address constant MATEZ_STAKING_PROG = 0x326FB70eF9e70f8f4c38CFbfaF39F960A5C252fa;
address constant MATEZ_TOKEN = 0x010C0D77055A26D09bb474EF8d81975F55bd8Fc9;

contract Matez is BaseTestWithBalanceLog {
    uint256 blocknumToForkFrom = 44222632 - 1;

    function setUp() public {
        vm.createSelectFork("bsc", blocknumToForkFrom);
        //Change this to the target token to get token balance of,Keep it address 0 if its ETH that is gotten at the end of the exploit
        fundingToken = MATEZ_TOKEN;
    }

    function testExploit() public balanceLog {
        //implement exploit code here

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-11/Matez_exp.sol_
