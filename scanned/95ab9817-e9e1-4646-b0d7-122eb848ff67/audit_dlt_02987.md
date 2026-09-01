# [?] Projekt Reward Vault - Permissionless purchase-tracking self-dealing

## Summary
Severity: Unknown
Chain: Ethereum
Component: ProjektRewardVault
Published: 2026-07-25
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-07/ProjektRewardVault_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~301.7 ETH

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

// Projekt (GREEN / GOLD) reward-vault drain — fake-purchase allocation, no ETH ever paid.
//
// Incident tx : 0x90f40d3c3b60370f7287d51d972ef54596c46e98f21af91b03a4e84c5e410f64
//   Ethereum mainnet block 25606412. The transaction is a raw CREATE (to == null): the
//   attacker EOA 0x61e7ad696215688d274c729a4cd0fbbc88fc4f85 deploys a contract whose entire
//   exploit runs inside the constructor. The deployed contract lands at
//   0x12d6fe4822325bba82faf6cf706e6b6885c922f9. There are no follow-up calls — the drain,
//   the flash-loan repay and the profit sweep all happen in that one deployment.
//
// Root cause (contract-logic bug, NOT an oracle / signature / privileged-key issue):
//   The reward vault 0x574fc478bc45ce144105fa44d98b4b2e4bd442cb (unverified) exposes a
//   permissionless trackPurchase(buyer) that credits an ETH allocation sized from the buyer's
//   memecoin token-balance DELTA, but never checks that any real ETH was actually spent to
//   acquire those tokens. The attacker:
//     1. flash-borrows ~14K WETH from Morpho,
//     2. pushes it into dozens of Uniswap V2 memecoin pairs and skim()s the resulting tokens
//        back to its own address, manufacturing large "purchase" balance deltas for free,
//     3. calls the permissionless trackPurchase to register the inflated allocations,
//     4. repays the Morpho flash loan in the same tx (net memecoin cost ~ zero),
//     5. calls massWithdraw(), which pays out msg.sender.transfer(allocation) in ETH.
//   Because the self-dealing skims size the allocation arbitrarily, the payout drains the
//   vault's ETH reward pool. No price is signed, no oracle is moved, no privileged key is used —
//   every step is an ordinary permissionless call reachable by any EOA. Confirmed from the
//   on-chain trace: a single fresh EOA (0.02 ETH balance), a pure CREATE, and only
//   permissionless vault / DEX / flash-loan entrypoints in the call tree.
//
// Verified on-chain ETH movement in the drain tx (block 25606412):
//   vault 0x574f..42cb   400.662320 ETH -> 98.957635 ETH   (net -301.70468 ETH drained)
//   vault -> deployed contract, in 13 massWithdraw tranches, gross 301.70468 ETH
//   deployed contract selfdestructs at the end, sweeping 300.70468 ETH to the profit wallet
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-07/ProjektRewardVault_exp.sol_
