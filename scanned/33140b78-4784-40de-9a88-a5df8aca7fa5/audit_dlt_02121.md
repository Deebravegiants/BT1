# [?] Balancer Protocol - Token Incompatible

## Summary
Severity: Unknown
Chain: Ethereum
Component: Balancer_20200628
Published: 2020-06-28
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2020-06/Balancer_20200628_exp.sol
Type: defi-exploit-poc

## Details
```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

import "forge-std/console2.sol";
import "forge-std/Test.sol";
import "../interface.sol";

/*
Balancer STA Exploit

Vulnerability principle: The incompatibility issue of deflationary tokens(STA) on Balancer. When users exchange deflationary tokens,
the contract does not validate the received tokens, leading to incorrect balance records.

Attackers can exploit this to create price deviations and profit from them. Exploitation process:
1. The attacker borrows a large amount of WETH from DYDX through flash loans.
2. The attacker continuously calls the swapExactAmountIn function to control the amount of STA tokens in the Balancer pool to 1,
    thereby increasing the price of STA for exchanging other tokens.
3. The attacker exchanges 1 STA for WETH and after each exchange, calls the gulp function to overwrite the STA balance,
    keeping the price high for STA to WETH exchanges.
4. Repay the flash loan and exit with profits.

Attack Tx: https://etherscan.io/tx/0x013be97768b702fe8eccef1a40544d5ecb3c1961ad5f87fee4d16fdc08c78106
*/

struct AccountInfo {
    address owner; // The address that owns the account
    uint256 number; // A nonce that allows a single address to control many accounts
}

interface IUniswapV2Router02 {
    function swapExactTokensForTokens(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external returns (uint256[] memory amounts);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2020-06/Balancer_20200628_exp.sol_
