# [?] Sodium - ERC-4337 Session-Key Validation Bypass

## Summary
Severity: Unknown
Chain: Arbitrum
Component: Sodium
Published: 2026-07-12
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-07/Sodium_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~11.76 ETH (~$21,200)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

// Sodium (ERC-4337 ZK/MPC smart wallet) — session-key validation-bypass + EntryPoint
// gas-deposit griefing. ~11.76 ETH (~$21.2k) drained from 300+ wallets in ONE tx, Arbitrum.
//
// Root cause: `_validateSignature` on the `executeWithSodiumAuthSession` path returns
// "valid" whenever `sessionKey == signer` and no safe-session is set — it never verifies
// the session-add auth proof (that check only runs later, in execution, not validation).
// Attacker signs userOps with its own EIP-1271 contract (isValidSignature always true) and
// a self-chosen sessionKey, so validateUserOp passes for ~300 wallets it doesn't own.
// Each op sets maxFeePerGas ~4062 gwei (~400,000x normal) with callGasLimit=0 and a
// deliberate out-of-gas on execution, so EntryPoint charges ~0.5 ETH of each wallet's
// gas deposit to the attacker (beneficiary) per op.
//
// Exploit tx: 0x738995176c3bbd22f8deabd7a1e6b89a044231781b39aa2f350897535e6d7bc1
// This was a CREATE tx (`to` is empty) — the entire attack runs inside the constructor
// of a one-shot contract, which loops all 300 victim wallets and self-destructs.
// Attacker/beneficiary: 0x7bD736631Afbe1d3795a94F60574f7fA0aE89347
//
// PoC strategy: fork one block before the exploit tx, prank the attacker address (the
// constructor hard-checks msg.sender == attacker), and deploy the EXACT creation bytecode
// via raw CREATE. The constructor replays the whole attack and self-destructs, exactly as
// it did on mainnet.
//
// Run: forge test --contracts ./src/test/2026-07/Sodium_exp.sol -vvv --evm-version cancun
// Requires an archive Arbitrum RPC (see foundry.toml [rpc_endpoints] "arbitrum").

interface IEntryPointV06 {
    function balanceOf(address account) external view returns (uint256);
}

contract SodiumExp is Test {
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-07/Sodium_exp.sol_
