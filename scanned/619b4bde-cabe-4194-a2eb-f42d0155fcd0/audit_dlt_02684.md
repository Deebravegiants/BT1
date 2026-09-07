# [?] OnyxDAO - Fake Market

## Summary
Severity: Unknown
Chain: Ethereum
Component: OnyxDAO
Published: 2024-09-26
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-09/OnyxDAO_exp.sol
Type: defi-exploit-poc

## Details
Lost: 4.1M VUSD, 7.35M XCN, 5K DAI, 0.23 WBTC, 50K USDT (>$3.8M USD)

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "forge-std/Test.sol";
import "../interface.sol";

// @KeyInfo - Total Lost : 4.1M VUSD, 7.35M XCN, 5K DAI, 0.23 WBTC, 50K USDT (>$3.8M USD)
// Attacker : https://etherscan.io/address/0x680910cf5fc9969a25fd57e7896a14ff1e55f36b
// Attack Contract :
//      - Main: https://etherscan.io/address/0xa57eda20be51ae07df3c8b92494c974a92cf8956
//      - Rate Manipulator: https://etherscan.io/address/0xae7d68b140ed075e382e0a01d6c67ac675afa223
//      - Fake oTokenRepay: https://etherscan.io/address/0x4f8b8c1b828147c1d6efc37c0326f4ac3e47d068
//      - Fake underlying: https://etherscan.io/address/0x3f100c9e9b9c575fe73461673f0770435575dc0e
//      - Fake oTokenCollateral: https://etherscan.io/address/0xad45812c62fcbc8d54d0cc82773e85a11f19a248
// Vulnerable Contract : (NFTLiquidation) https://etherscan.io/address/0xf10bc5be84640236c71173d1809038af4ee19002
// Attack Tx : https://etherscan.io/tx/0x46567c731c4f4f7e27c4ce591f0aebdeb2d9ae1038237a0134de7b13e63d8729
// @Info
// Vulnerable Contract Code : https://etherscan.io/address/0xf10bc5be84640236c71173d1809038af4ee19002#code
// L671-678, liquidateWithSingleRepay() function
// @POC Author : [rotcivegaf](https://twitter.com/rotcivegaf)

// Contracts involved
address constant balancerVault = 0xBA12222222228d8Ba445958a75a0704d566BF2C8;
address constant weth = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
address constant oETH = 0x2CCb7d00a9E10D0c3408B5EEfb67011aBfaCb075;
address constant Unitroller = 0xcC53F8fF403824a350885A345ED4dA649e060369;
address constant oXCN = 0xBD20ae088deE315ace2C08Add700775F461fEa64;
address constant oDAI = 0xF3354d3e288CE599988e23f9ad814Ec1b004d74a;
address constant oBTC = 0x7a89e16Cc48432917C948437AC1441b78D133A16;
address constant oUSDT = 0x2C6650126B6E0749f977D280c98415ed05894711;
address constant oVUSD = 0xeE894c051c402301bC19bE46c231D2a8E38b0451;
address constant VUSD = 0x0BFFDD787C83235f6F0afa0Faed42061a4619B7a;
address constant NFTLiquidationProxy = 0x323398DE3C35F96053D930d25FE8d92132F83d44;
address constant uniV3Router = 0xE592427A0AEce92De3Edee1F18E0157C05861564;

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-09/OnyxDAO_exp.sol_
