# [?] ExchangeIssuance (Index Coop) - TOCTOU positionMultiplier inflation via malicious pre-issue hook

## Summary
Severity: Unknown
Chain: Ethereum
Component: ExchangeIssuance
Published: 2026-07-30
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-07/ExchangeIssuance_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~9.6K USD (~$8,174 recovered value on-chain)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

// Index Coop ExchangeIssuance drain via attacker-crafted SetToken NAV manipulation.
//
// Incident tx : 0x7f45428df558fba1d19ab115effef8ecd1e6e05b491f02202b0815e47b8d658b
//   Ethereum mainnet block 25644621. The attacker EOA 0x0736930a signs three sequential txs
//   in this same block:
//     tx0 (nonce 0, CREATE)      -> deploys the orchestrator/"valuer" contract at
//                                   0x388a3Da3...994802.
//     tx1 (nonce 1, -> 0x388a..) -> setup: deploys the malicious SetToken (BHSET) at
//                                   0xf7c2d0a2...06948 through the real Set Protocol
//                                   SetTokenCreator, wires the attacker-controlled manager/hook
//                                   0x8f449d85...a26c58 and a custom NAV valuer, initialises the
//                                   BasicIssuanceModule + CustomOracleNavIssuanceModule.
//     tx2 (nonce 2, -> 0x388a..) -> THIS exploit call (calldata replayed below).
//   Forking at the tx2 hash makes foundry replay tx0 and tx1 first, so the orchestrator, the
//   SetToken and the manager already exist at the exact on-chain addresses before the drain.
//
// Root cause (attacker-deployed-contract on-chain state manipulation, NOT a compromised
// signer / admin key). Every privileged role in the flow -- the SetToken's manager, its
// pre-issue hook, and its NAV valuer -- is a contract the attacker deployed in this same
// block. No Index Coop key, no privileged EOA, and no signature is involved. Confirmed from
// the trace: the only externally-owned account in the call tree is the attacker EOA, and it
// merely calls its own orchestrator.
//   Index Coop's ExchangeIssuance.issueSetForExactToken trusts arbitrary SetToken state with
//   no lock between the quote read and the settlement transfer. It reads getComponents() and
//   getDefaultPositionRealUnit() to size the trade, but the SetToken's positionMultiplier was
//   inflated (~93.66x) mid-flow by the attacker's manager firing a fake NAV issue/redeem
//   valuation through the CustomOracleNavIssuanceModule. When BasicIssuanceModule.issue then
//   settles, it reads the inflated *real* units and pulls ExchangeIssuance's OWN component
//   inventory (LINK/UNI/AAVE/MKR/WBTC/HEX/BIT/USDC/WETH) into the SetToken -- a TOCTOU between
//   the units read for pricing and the units used for the transferFrom.
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-07/ExchangeIssuance_exp.sol_
