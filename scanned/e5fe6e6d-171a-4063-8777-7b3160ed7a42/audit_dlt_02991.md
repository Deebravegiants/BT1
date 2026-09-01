# [?] UnprotectedArbBot - Unprotected arbitrary-call forwarder drained via pre-granted WETH allowance

## Summary
Severity: Unknown
Chain: Base
Component: UnprotectedArbBot
Published: 2026-07-30
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-07/UnprotectedArbBot_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~16.623 WETH (~$31.7K)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

// UnprotectedArbBot — unprotected arbitrary-call forwarder drained via a pre-granted WETH allowance
// ~16.623 WETH (~$31.7K at $1904.74/WETH) pulled from an owner EOA on Base in a single tx.
//
// Exploit tx : 0xe831f3991132cbaffbb4a3738da7d1e254a6c02f0adce605a333229a61e27ad7 (block 49304016)
//   Contract-creation tx: the attacker EOA deploys an orchestrator (0x45e7...15cC) whose
//   constructor deploys a helper (0x797c...6dc8) and immediately drives the drain. The helper
//   makes ONE call to the victim's unprotected selector 0x42be3129.
//
// Root cause (reproduced observable behavior — victim is UNVERIFIED, names are apparent only):
//   The victim contract 0xa317...c170 exposes selector 0x42be3129 with NO access control. It
//   takes a caller-supplied target + calldata, executes it via a low-level CALL, then sweeps the
//   named token balance to msg.sender. A separate selector (0x23a69e75) IS onlyOwner-gated
//   (its handler reverts "not owner" on `msg.sender != owner`), but 0x42be3129 is not gated at
//   all. The attacker abused this to make the victim call
//     WETH.transferFrom(owner, victim, 16.623 WETH)
//   using an allowance the owner had PRE-GRANTED the victim, then the same 0x42be3129 call swept
//   that WETH out to the caller (the helper), which forwarded it to the attacker EOA.
//
//   Confirmed attacker-controlled + on-chain: no signature, no privileged role, no compromised
//   key, no upstream privilege upgrade. The victim call in the trace has msg.sender = the
//   attacker-deployed helper (not the owner), and the tx is a plain contract creation from the
//   attacker EOA. The only pre-existing state relied upon is the owner's ERC20 allowance to the
//   victim, which is standard on-chain state, not a privilege.
//
// Observed on-chain (drpc callTracer + receipt logs), single 0x42be3129 call:
//   1. victim -> WETH.transferFrom(helper, WETH, 0)                 (incidental, amount 0)
//   2. victim -> WETH.transferFrom(owner, victim, 16.623 WETH)      (the arbitrary forwarded call)
//   3. victim -> WETH.transfer(helper, 16.623 WETH)                 (sweep to caller)
//   then helper -> WETH.transfer(attacker, 16.623 WETH)             (forward to attacker EOA)
//
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-07/UnprotectedArbBot_exp.sol_
