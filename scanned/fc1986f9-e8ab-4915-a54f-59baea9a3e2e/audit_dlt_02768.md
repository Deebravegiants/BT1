# [?] Pump - Not Slippage Protection

## Summary
Severity: Unknown
Chain: BNB Chain
Component: Pump
Published: 2025-03-04
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-03/Pump_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~ $6.4K

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "../basetest.sol";
import "../interface.sol";

// @KeyInfo - Total Lost : ~ 11.29 BNB ($6.4K)
// Attacker : https://bscscan.com/address/0x5d6e908c4cd6eda1c2a9010d1971c7d62bdb5cd3
// Attack Contract : https://bscscan.com/address/0x0e220c6c52d383869a5085ef074b6028254b3462
// Vulnerable Contract : TAGAIFUN, GROK, PEPE, TEST ... TokenContract
// Attack Tx : https://bscscan.com/tx/0xdebaa13fb06134e63879ca6bcb08c5e0290bdbac3acf67914c0b1dcaf0bdc3dd

// @Info
// Vulnerable Contract Code :
//  - TAGAIFUN: https://bscscan.com/address/0x09762e00ce0de8211f7002f70759447b1f2b1892#code
//  - GROK: https://bscscan.com/address/0x02e8ead6de82c8a248ef0eebe145295116d0e4c2#code
//  - PEPE: https://bscscan.com/address/0x6b7e9be56ca035d3471da76caa99f165449697a0#code
//  - TEST: https://bscscan.com/address/0xba0d236fbcbd34052cdab29c4900063f9efe6e4f#code

// @Analysis
// Post-mortem : N/A
// Twitter Guy : https://x.com/TenArmorAlert/status/1897115993962635520
// Hacking God : N/A

address constant WBNB_ADDR = 0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c;
address constant BSC_USD = 0x55d398326f99059fF775485246999027B3197955;
address constant TAGAIFUN_TOKEN = 0x09762e00Ce0DE8211F7002F70759447B1F2b1892;
address constant GROK_TOKEN = 0x02E8eAd6De82c8a248eF0EebE145295116D0E4C2;
address constant PEPE_TOKEN = 0x6B7e9Be56cA035D3471dA76caa99f165449697A0;
address constant TEST_TOKEN = 0xBA0D236FbcbD34052CdAB29c4900063F9Efe6E4f;
address constant PANCAKE_V3_POOL_BUSD_WBNB = 0x172fcD41E0913e95784454622d1c3724f546f849;
address constant PANCAKE_V2_FACTORY = 0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73;
address constant PANCAKE_V2_ROUTER = 0x10ED43C718714eb63d5aA57B78B54704E256024E;

contract Pump_exp is BaseTestWithBalanceLog {
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-03/Pump_exp.sol_
