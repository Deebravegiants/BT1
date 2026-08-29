# [?] StrongBlock - Governance takeover of abandoned Governor

## Summary
Severity: Unknown
Chain: Ethereum
Component: StrongBlock
Published: 2026-08-05
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-08/StrongBlock_exp.sol
Type: defi-exploit-poc

## Details
Lost: 32,695.76 STRONG + 383,447.17 STRNGR (~$72K)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

// StrongBlock — governance takeover of an abandoned on-chain Governor, then abuse of
// the seized proxy-upgrade authority to swap a fund-holding proxy's implementation and
// sweep the treasury. ~32,695 STRONG + ~383,447 STRNGR drained on Ethereum (~$72K).
//
// Attacker EOA: 0xACBCa357981870f30130B145762d671891CA810c
// Victim (StrongBlock Governor, admin of the Upgrader): 0xBDDC7Ef8BaCeacE16DCE005102639a4bB86CB8C1
// Upgrader (Compound-style admin controlling the proxies): 0x75C53809A047c3d422B91Eda50A20914fBe91C61
// Service proxy that HELD the tokens (OZ AdminUpgradeabilityProxy): 0x53cA51Ba980B6475C13d158c1825013cf81038Fc
// Attacker-deployed malicious implementation: 0xe89C0d3FcE4EB31060b6a0329bA408029D0c4106
//
// Root cause (governance capture, verified on-chain, same class as the CompoundProvider /
// BarnBridge precedent already in this repo):
//   - The Upgrader (0x75C5) is admin of the StrongBlock proxies. Its admin was the Governor
//     0xBDDC. The Governor's vote token (STRONG) is near worthless and the DAO abandoned, so
//     the attacker acquired majority voting weight on the open market, then pushed a proposal
//     through the Governor's own propose/vote/queue/execute flow calling setPendingAdmin(attacker)
//     on the Upgrader. That is settled on-chain before this replay: at block 25691518,
//     Upgrader.admin() == Governor 0xBDDC and Upgrader.pendingAdmin() == attacker EOA. No stolen
//     key or signature anywhere — the attacker became privileged through the DAO's own machinery.
//   - The value-loss sequence (attacker EOA tx nonces, all on-chain):
//       n0  block 25691471  deploy malicious impl 0xe89c0d3f
//       n1  block 25691519  Upgrader.acceptAdmin()                 -> attacker becomes Upgrader admin
//       n2  block 25691525  Upgrader.upgrade(serviceProxy, malImpl)-> service proxy now malicious
//       n3  block 25691527  serviceProxy.run() [selector 0xc0406226] -> sweeps STRONG+STRNGR to caller
//     Later, in a separate tx (nonce 23, the hash originally provided,
//     0x92be5e374e260192f8fdb5ffdc33504c768ecad091cc7dbc37282e5ca8ea94c6), the same upgrade
//     primitive was applied to the Governor proxy 0xBDDC itself. That governor proxy holds no
//     STRONG/STRNGR, so it is not the fund-loss tx; the ~$72K loss is the service-proxy drain above.
//
// The malicious impl is unverified, so run() (0xc0406226) and its attacker-gating are treated as
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-08/StrongBlock_exp.sol_
