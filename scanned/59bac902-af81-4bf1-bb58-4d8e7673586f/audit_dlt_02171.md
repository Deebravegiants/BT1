# [?] Agave Finance - ERC667 Reentrancy

## Summary
Severity: Unknown
Chain: EVM
Component: Agave
Published: 2022-03-15
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-03/Agave_exp.sol
Type: defi-exploit-poc

## Details
```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "./../basetest.sol";
import "./../interface.sol";

interface IGnosisBridgedAsset is IERC20 {
    function mint(address, uint256) external returns (bool);
}

// @KeyInfo - Total Lost : ~1.5M US$
// Attacker : https://gnosisscan.io/address/0x0a16a85be44627c10cee75db06b169c7bc76de2c
// Attack Contract : https://gnosisscan.io/address/0xF98169301B06e906AF7f9b719204AA10D1F160d6
// Vulnerable Contract : https://gnosisscan.io/address/0x207E9def17B4bd1045F5Af2C651c081F9FDb0842 (Agave lending pool v1)
// Attack Tx : https://gnosisscan.io/tx/0xa262141abcf7c127b88b4042aee8bf601f4f3372c9471dbd75cb54e76524f18e

// @Info
// Vulnerable Contract Code : https://github.com/Agave-DAO/protocol-v2/commit/31922797ba110ddb3e908936b940b40221b7e190#diff-d237d9f48e3d6657a5f94c89b903c5003cba6f9a286e26eff509cb44a3f4ee8f

// @Analysis
// Post-mortem :https://medium.com/agavefinance/agave-exploit-reentrancy-in-liquidation-call-51ae407bc56
// Twitter Guy : https://twitter.com/Mudit__Gupta/status/1503783633877827586

/*
Detailed explanation of the agave exploit attack flow:

1. Prepare Phase:
   - Initial Condition: Ensure that the health factor is slightly above 1.
   - Transition: Advance time by one hour after the initial prepare.
   - Objective: Reduce the health factor to less than 1 in the next block.
   - Purpose: This step is essential for the liquidation call to work, as it requires a health factor below 1.

2. Flashloan and Deposit Phase:
   - Action: Execute a flashloan and deposit tokens.
   - Exploited Assets: In this exploit, withdraw and borrow all funds from WETH and maximize borrowing from all available pools.

3. Exploit Completion:
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-03/Agave_exp.sol_
