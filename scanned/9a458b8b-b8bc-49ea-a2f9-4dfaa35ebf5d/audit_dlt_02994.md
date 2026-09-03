# [?] AllbridgeCCTP - Phantom CCTP deposit via unverified message attestation

## Summary
Severity: Unknown
Chain: Base
Component: AllbridgeCCTP
Published: 2026-08-19
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-08/AllbridgeCCTP_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~190,155.98 USDC drained (net attacker profit ~189,751.55 USDC after flash-loan premium; router retained its 1,000 USDC fee)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

// Allbridge (Core / cross-chain Router + CCTP integration) — Base
// 190,156 USDC drained from the Router in a single Base tx (its full 191,156 USDC balance minus the
// 1,000 USDC / 0.1% fee the Router kept).
// Attacker nets 189,751.554381 USDC after a 404.42 USDC Aave flash-loan premium.
//
// Exploit tx   : 0x9f906fcd8fceaa6745e8d1c004861dcfa9b5e6a893fe1e8c5d0013a4e982e6a8 (block 50157345)
// Forged msg tx: 0x2a88d79756b4547b33fea7b3c1420793680e2b8952bef4c65e99879e16b22140 (Polygon, 24 days earlier)
// Attacker EOA : 0x2419432344b0B892E592b2601B98eaE702Ba360e (nonce 8 at exploit time)
// Harness ctrt : 0xb6fBDFA5F3CBEB139D4ccE86D92F4ac8687B16c0 (deployed 25 days earlier; profit sink)
// Logic ctrt   : 0xe9edf1582ed9520f7149669d9c6bf3276b02477e (CREATE'd in-tx from the harness call)
// Victim Router: 0xaA119F7442eCC28b9a8F236707ADA8362CFF24fF
// Vuln messenger (CCTPTokenMessenger): 0xf9b710e427bf4d93598e0f80a84de22c7ad9b577
// MessageTransmitterV2 (Circle)      : called by the messenger during receiveCctpMessage
//
// Root cause (reproducible contract mechanism, verified against the on-chain trace; NOT a
// key/signer/privileged path — every call below is permissionless):
//   CCTPTokenMessenger.receiveCctpMessage(message, attestation) relays an attested Circle
//   message through MessageTransmitterV2.receiveMessage, then credits
//       receivedMessages[messageHash] = amount - feeExecuted
//   using the amount field read DIRECTLY FROM THE MESSAGE BODY, with no check that the message
//   actually caused a USDC mint. Circle's MessageTransmitterV2.sendMessage is a GENERIC
//   attestation primitive (no burn/mint attached): anyone can author a payload shaped like a CCTP
//   deposit and have Circle legitimately attest it — Circle only signs that the message was
//   submitted, not that value moved. The messenger's sourceSender guard compares against
//   remoteTokenMessengers[sourceChainId], a value readable on-chain by anyone, so the attacker
//   simply copied it into the forged body. The forged message's recipient was the attacker's own
//   contract (not Circle's minting TokenMessengerV2), so nothing was minted — but the messenger
//   never checks that field or observes any balance change, so it still credited the phantom
//   deposit. The Router's receiveToken uses receivedTokenAmount(messageHash) > 0 as its ONLY
//   solvency test and pays out the caller-supplied normalized amount.
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-08/AllbridgeCCTP_exp.sol_
