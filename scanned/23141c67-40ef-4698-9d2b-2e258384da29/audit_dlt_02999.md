# [?] PantherBase - Reality.eth governance timeout exploit (pre-production Base deployment, no user funds)

## Summary
Severity: Unknown
Chain: Base
Component: PantherBase
Published: 2026-08-06
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-08/PantherBase_exp.sol
Type: defi-exploit-poc

## Details
Lost: 5,124,773.63 ZKP + 0.1233 ETH (Panther Base pre-launch deployment, not live user funds)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

// Panther Protocol (ZKP) — governance-timeout capture on the BASE deployment.
//
// IMPORTANT FRAMING: Panther's Base deployment was NOT yet in production at the time of this
// incident. Per the team's own public (Telegram) statement, no live user funds were compromised;
// this was a pre-launch governance-mechanism failure, not a drain of an operating protocol. The
// on-chain value that moved (~5.12M ZKP + ~0.12 ETH) came out of the pre-launch deployment's own
// governance-controlled proxies, and the root cause was a missing safeguard on THIS deployment
// (the Reality.eth module was not disabled while there was no active governance proposal), a
// protection the team indicated was correctly enabled on their other deployments.
//
// Same class as the StrongBlock / CompoundProvider (BarnBridge) PoCs already in this repo:
// governance capture of a proxy-upgrade authority, then abuse of that authority to swap fund-
// holding proxies to a drainer implementation. The twist here is that NO code bug and NO stolen
// key were involved. The path is entirely permissionless: anyone can (1) submit a Reality.eth /
// Zodiac governance proposal, (2) bond a "yes" answer to their own proposal, and (3) execute it
// once finalized. The only thing the attacker exploited was that nobody posted a competing "no"
// bond inside the challenge window, so an unopposed self-answer finalized and executed.
//
// ---- Actors / contracts (all verified on-chain, Base / chainId 8453) ----
// Attacker EOA:            0x7dB4cFea07042ca13a8E26cC90BbB59982Fe95B6
// Attacker orchestrator:   0x9400161d512C740e1C0C77f3c931D112f068210c  (owner() == attacker EOA)
//                          its initiate() both ASKED the proposal question and self-answered "yes"
//                          with the 0.5 ETH bond, and it is the recipient of the drained funds.
// Zodiac RealityModuleETH: 0x4ce69e77A8806B51f15b8D0FC38A9c1f66A851b4  (EIP-1167 clone of
//                          impl 0x4e35da39fA5893a70A40Ce964F993d891E607cC0)
//   avatar/target/owner == Panther Safe 0xb16283A233D5b010A7b290d593847207495F0284
//   oracle              == Reality.eth  0x2F39f464d16402Ca3D8527dA89617b73DE2F60e8
//   questionTimeout 43200 (12h)  questionCooldown 28800 (8h)  minimumBond 0.5 ETH
//   (the 12h + 8h challenge/cooldown window the report cites — read live from the module)
// Reality.eth v3.0:        0x2F39f464d16402Ca3D8527dA89617b73DE2F60e8
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-08/PantherBase_exp.sol_
