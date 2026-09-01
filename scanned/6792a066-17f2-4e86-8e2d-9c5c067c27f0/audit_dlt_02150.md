# [?] Popsicle - Repeated Reward Claim - Logic Flaw

## Summary
Severity: Unknown
Chain: Ethereum
Component: Popsicle
Published: 2021-08-04
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-08/Popsicle_exp.sol
Type: defi-exploit-poc

## Details
```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.15;

import "../basetest.sol";
import "forge-std/interfaces/IERC20.sol";

// @KeyInfo - Total Lost : 20M USD
// Attacker : https://etherscan.io/address/0xf9E3D08196F76f5078882d98941b71C0884BEa52
// Attack Contract : https://etherscan.io/address/0xdFb6faB7f4bc9512d5620e679E90D1C91C4EAdE6
// Vulnerable Contract : https://etherscan.io/address/0xc4ff55a4329f84f9Bf0F5619998aB570481EBB48
// Attack Tx : https://etherscan.io/tx/0xcd7dae143a4c0223349c16237ce4cd7696b1638d116a72755231ede872ab70fc

// @Info
// Vulnerable Contract Code : https://etherscan.io/address/0xc4ff55a4329f84f9Bf0F5619998aB570481EBB48#code

// @Analysis
// Post-mortem : https://blocksecteam.medium.com/the-analysis-of-the-popsicle-finance-security-incident-9d9d5a3045c1
// Twitter Guy : https://twitter.com/BlockSecTeam/status/1422786223156776968
// Hacking God : https://twitter.com/BlockSecTeam/status/1422786223156776968

// Simple SafeERC20 implementation
library SafeERC20 {
    function safeTransfer(IERC20 token, address to, uint256 value) internal {
        (bool success, bytes memory data) = address(token).call(
            abi.encodeWithSelector(token.transfer.selector, to, value)
        );
        require(success && (data.length == 0 || abi.decode(data, (bool))), "SafeERC20: transfer failed");
    }

    function forceApprove(IERC20 token, address spender, uint256 value) internal {
        (bool success, bytes memory data) = address(token).call(
            abi.encodeWithSelector(token.approve.selector, spender, value)
        );
        require(success && (data.length == 0 || abi.decode(data, (bool))), "SafeERC20: approve failed");
    }
}

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-08/Popsicle_exp.sol_
