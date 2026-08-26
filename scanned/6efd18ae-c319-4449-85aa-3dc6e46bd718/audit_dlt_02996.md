# [?] FlashstakeV2 - Mispriced reward pool, instant upfront reward extraction

## Summary
Severity: Unknown
Chain: Ethereum
Component: FlashstakeV2
Published: 2026-08-20
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-08/FlashstakeV2_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~0.5453 WETH drained (28.25% of reward pool reserve); attacker net profit ~0.4285 ETH

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

// Flashstake V2 — mispriced upfront-reward extraction from the FLASH/WETH reward pool — Ethereum
// ~0.55 WETH drained from the reward pool; attacker net profit ~0.4284 ETH (~$696) in one tx.
//
// Exploit tx  : 0xe3a7bd727174526096ebb51672cd3f801fc03ff984d351673373df6b0c166393 (block 25798654)
// Caller EOA  : 0xa521f8c249eb055796B765642Eed78c01CD620D1 (nonce 1, plain EOA, tx.origin)
// Attack ctrt : 0xfA9D717678DdAf60A123c6Ba0506521e923793d0 (entry, selector 0xb4969dfa)
// Victim pool : 0xC9fc5a6007c9801ebae1813D4D03208C4E85be44 (Flashstake FLASH/WETH reward pool)
//
// Protocol addresses touched:
//   FlashProtocol : 0x15EB0c763581329C921C8398556EcFf85Cc48275 (stake entry point)
//   FlashApp      : 0xb0aeae6E204Bd95911EaD25263d7078954fb7fB0 (reward receiver; also AMP->FLASH converter)
//   FLASH (new)   : 0x20398aD62bb2D930646d45a6D4292baa0b860C1f
//   AMP (legacy)  : 0xfF20817765cB7f73d4bde2e66e067E58D11095C2 (converted 1:1-ish into FLASH)
//   WETH          : 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2
//   Uni V4 Mgr    : 0x000000000004444c5dc75cB358380D2e3dE08A90 (native-ETH flash source via unlock/take/settle)
//   DODO pool     : 0x4D48078Fa76D2CebCfde0d20a0Dc2d7E5373EefE (WETH->FLASH)
//   Uni V2 pair   : 0x08650bb9dc722C9c8C62E79C2BAfA2d3fc5B3293 (WETH->AMP)
//   Uni V2 pair   : 0x31d9b2D096C7aBD1Cf9a3CC8f1982E5FFCA09C47 (WETH->FLASH)
//
// Root cause (reproducible contract mechanism, verified against the on-chain trace, NOT a
// key/signer/privileged-claim compromise):
//   FlashProtocol.stake() computes the minted FLASH reward purely from the deposited FLASH
//   quantity, the lock duration and the protocol's own FLASH balance / total supply
//   (getFPY reads only balanceOf(protocol) and totalSupply()). FLASH is never valued against any
//   external market price. When FlashApp is passed as the reward receiver (_fTokenTo), stake()
//   mints the upfront reward straight to FlashApp and calls FlashApp.receiveFlash(), which
//   immediately forwards the freshly minted FLASH into the FLASH/WETH reward pool and calls the
//   pool's stakeWithFeeRewardDistribution(), paying out real WETH to the attacker in the same call.
//   So cheaply-acquired FLASH (bought on the open market + legacy AMP converted to FLASH) is locked
//   to mint upfront reward FLASH at the protocol's internal unit-based rate, then that reward is
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-08/FlashstakeV2_exp.sol_
