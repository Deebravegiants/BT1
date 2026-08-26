# [?] AIC - Pair skim / reserve-mismatch exploit (flash-swap leveraged)

## Summary
Severity: Unknown
Chain: EVM
Component: AIC
Published: 2026-08-03
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-08/AIC_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~32.36 BNB (~$21.5K)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

// AIC — PancakeSwap-pair skim() reserve-mismatch drain, flash-swap leveraged, on BNB Chain
// ~32.36 BNB (~$21.5K) netted by the attacker EOA in a single CREATE transaction.
//
// Exploit tx : 0x905cc861bcc525d3a8e699583943831b97500bbac11c92dc20ed6edbddd69f87 (block 113782392)
//   The tx has NO `to` field: it is a raw CONTRACT-CREATION. The EOA deploys the outer
//   "factory" contract 0xf0f74b90afb29903c80ed7531b50764c49089e25, whose CONSTRUCTOR in turn
//   CREATEs the child attack contract 0x29977d9b8a888b17bffa2958b003956a5e8be69a and
//   immediately calls its entry selector 0x28022411 on it. The whole exploit therefore runs
//   inside the deployment of that single tx — there is no second call, no separate withdraw tx.
//
// Root cause (reproducible contract mechanism, NOT a key/signer/privileged-claim compromise):
//   AIC is a fee-on-transfer token. Its NEX/AIC PancakeSwap pair 0x974c...ddc75 had accumulated
//   AIC balance ABOVE the pair's recorded reserve (the fee-on-transfer surplus never got
//   synced into the reserves). skim() on a Uniswap-V2-style pair is PUBLIC and pays out the
//   difference between the token balance and the recorded reserve to any caller. The attacker:
//     1. flash-swaps 42.98M AIC out of the USDC/AIC pair 0xe89636...96415 (pancakeCall path),
//     2. cycles AIC <-> NEX through the NEX/AIC pair to inflate that pair's untracked AIC surplus,
//     3. calls the PUBLIC skim() on the NEX/AIC pair to extract 83.26M AIC of excess balance,
//     4. repays 43.09M AIC to close the flash swap,
//     5. dumps the remaining ~40.17M AIC for 21,504 USDC, routes USDC -> WBNB, unwraps to BNB.
//   Every step is a permissionless public function (flash swap, skim, swap) driven entirely by
//   attacker-controlled on-chain state. No owner key, no admin role, no privileged path.
//   (A separate ~2.03M NEX residue ends up at helper 0x0f7e35653f6a8e09a0865a183b51177e16237cb5;
//    it is not part of the EOA's BNB gain and is out of scope for the assertion below.)
//
// The child contract stamps tx.origin (opcode 0x32) as its owner at deploy time and forwards
// the unwrapped BNB to that owner inside the same tx. Faithful reproduction: fork at block-1
// (before the exploit, where the fee-on-transfer surplus already sits on the pair) and re-issue
// the EXACT original creation bytecode via a raw CREATE, pranking the attacker EOA as BOTH
// msg.sender AND tx.origin so the child pays the profit back to the EOA. Bytecode is hardcoded
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-08/AIC_exp.sol_
