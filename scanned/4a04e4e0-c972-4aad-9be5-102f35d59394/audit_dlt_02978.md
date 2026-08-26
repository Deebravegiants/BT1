# [?] CrowdRingCircle - Reserve Manipulation via burn-from-pair + sync

## Summary
Severity: Unknown
Chain: BNB Chain
Component: CrowdRingCircle
Published: 2026-07-16
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-07/CrowdRingCircle_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~201,359 USDT

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

// CrowdRingCircle (CRC) — "sell destroy" reserve-burn price manipulation on BNB Chain
// ~$201K USDT drained from the CRC/USDT PancakeSwap LP.
//
// Exploit tx : 0xeaef22325e02ac65a8e1f2e1a3a43f7b7ac8d2323ce6f698a90813e77017c834 (block 110301524)
//   The tx is a CREATE (empty `to`): the whole flash-loan attack runs inside the attacker
//   contract's constructor. Flash-funded via PancakeSwap Infinity Vault + Venus.
//
// Root cause: CRC's `_update` override has a "sell destroy" path. On any transfer TO a DEX pair it
//   burns CRC straight out of the pair's own balance (`_safeDeductBalance(to, amount)`) then calls
//   `IUniswapV2Pair(to).sync()`. Repeatedly pushing CRC into the LP forces the pair to burn its own
//   reserves and re-sync, skewing the ratio so CRC's price inflates; the attacker then swaps CRC
//   for USDT at the manipulated rate.
//
// CRC token  : 0x8581433150f2C48ff2efE5A22b17c7D405054509
// Victim LP  : 0xd8799A644850c065388C22Df4EE0C28472922526 (CRC/USDT PancakeSwap pair)
// Attacker   : 0x34579eA92a07a88F5505dFaA4D99Ab94b2784087
//
// Forensic replay: the exact creation bytecode is hardcoded below and re-deployed via raw CREATE
// at the historical fork block, pranking the attacker EOA as both msg.sender and tx.origin
// (the constructor guards on the ORIGIN opcode).
//
// Run:
//   forge test --contracts ./src/test/2026-07/CrowdRingCircle_exp.sol -vvv
//   (add `--evm-version cancun` if you hit a frameless [NotActivated] EvmError)
//   Requires an ARCHIVE BSC RPC mapped to the `bsc` rpc alias.

interface IERC20 {
    function balanceOf(address) external view returns (uint256);
}

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-07/CrowdRingCircle_exp.sol_
