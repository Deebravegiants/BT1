# [?] - BRA - Business Logic Flaw

## Summary
Severity: Unknown
Chain: BNB Chain
Component: BRA
Published: 2023-01-10
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-01/BRA_exp.sol
Type: defi-exploit-poc

## Details
Lost: 819 BNB (~224k$)
References:
- https://bscscan.com/address/0x449fea37d339a11efe1b181e5d5462464bba3752#code#L449-L457

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.17;

import "forge-std/Test.sol";
import "./../interface.sol";

// @KeyInfo - Total Lost : 819 BNB (~224K US$)
// Attacker : 0x67a909f2953fb1138bea4b60894b51291d2d0795
// Vulnerable Contract : 0x449fea37d339a11efe1b181e5d5462464bba3752

// @Info
// Attack Contract :
//  0x1fae46b350c4a5f5c397dbf25ad042d3b9a5cb07
//  0x6066435edce9c2772f3f1184b33fc5f7826d03e7
// Attack Txs :
//  0x6759db55a4edec4f6bedb5691fc42cf024be3a1a534ddcc7edd471ef205d4047 (profit 675 WBNB)
//  0x4e5b2efa90c62f2b62925ebd7c10c953dc73c710ef06695eac3f36fe0f6b9348 (profit 144 WBNB)
// Vulnerable Contract Code :
//  https://bscscan.com/address/0x449fea37d339a11efe1b181e5d5462464bba3752#code#L449-L457

// @Analysis
// Blocksec : https://twitter.com/BlockSecTeam/status/1612701106982862849

// Root cause : Business Logic Flaw
//  The BRA Token contract implements a tax logic in the _transfer() function.
//  When the sender/recipient is LP Pair, it will charge a double tax fee to LP Pair, but without called sync() functions.
//  That allows attackers to call the skim() function to collect all imbalanced amounts.
// Potential mitigations: Implements sync() function in _transfer()

contract Attacker is Test {
    WBNB constant wbnb = WBNB(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c);
    Exploit immutable exploit;

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-01/BRA_exp.sol_
