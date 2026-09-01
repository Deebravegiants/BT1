# [?] USM - defund() price split-invariance rounding exploit

## Summary
Severity: Unknown
Chain: Ethereum
Component: USM
Published: 2026-08-09
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-08/USM_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~70.83 ETH

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

// USM (Minimalist USD stablecoin) — split-invariance flaw in the FUM redemption curve.
// ~70.8 ETH drained on Ethereum, Aug 2026.
//
// Attacker EOA:       0xb92b2E47680c89DA8f951B8963ef469f461a50Fc
// Attacker contract:  0x5a5e29ba89663a3558273354E990426F3cAc7de7
// Victim (USM):       0x2a7FFf44C19f39468064ab5e5c304De01D591675
// FUM token:          0x86729873e3b88DE2Ab85CA292D6d6D69D548eDF3
// Flash lender:       Morpho Blue 0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb (WETH, 0 fee)
// Exploit tx:         0xfae5e751b8ce01457cbb6b529839f24a0cff50faaabcbd0fd02ca0cf559b050e (block 25716150)
//
// Root cause (verified against the on-chain trace of the exploit tx):
//   USM's defund() redeems FUM for ETH. The ETH paid for a redemption is priced off the
//   arithmetic mean of the CURRENT FUM sell price and the ESTIMATED FINAL FUM sell price after
//   the redemption, and each defund() also contracts internal state (adjShrinkFactor). That
//   averaging is not "split invariant": redeeming one large FUM amount in a single defund() pays
//   strictly LESS ETH than redeeming the same total FUM amount as many small equal slices across
//   consecutive defund() calls. The per-call state contraction plus integer rounding compound the
//   gap. The attacker minted a large FUM position with fund(), then redeemed it in 64 equal
//   slices instead of one, extracting more ETH than it paid in.
//
// This is a pure pricing/rounding logic bug, NOT price manipulation. The Chainlink/Uniswap TWAP
// oracle reads are identical before and during the attack (same latestPrice() return every call
// in the trace); nothing about the ETH/USD price is moved. The flash loan only supplies working
// capital to fund() a big FUM position — it is not used to move any price.
//
// Access check (confirmed from the trace): every fund() and defund() in the sequence is a plain
// permissionless public call made by the attacker contract inside the Morpho flash-loan callback.
// No signer, no admin role, no privileged path. fund(to, minFumOut) and defund(to, fumToBurn,
// minEthOut) are open to any caller.
//
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-08/USM_exp.sol_
