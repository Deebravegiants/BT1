# [?] Atomic - Flash-loan price oracle manipulation of lending collateral valuation

## Summary
Severity: Unknown
Chain: EVM
Component: Atomic
Published: 2026-08-07
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-08/Atomic_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~29,984.27 USDC

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

// Atomic (non-custodial leveraged trading + isolated "AtomicLending") — Arbitrum
// ~29,984 USDC drained by a fresh attacker EOA in a single transaction.
//
// Exploit tx  : 0xbd4a009cd609a05f1a64458969a1e2c2065472f0ee06a322246f155be12e3a9a (block 492104035)
// Attacker EOA: 0xf8803DaE13A6757E53711214769B5fb52Ec26C7E (nonce 1 at exploit time)
// Attack ctrt : 0x44d2D34E148e1Da5c4291C110f6ff0E472037255 (deployed by the EOA at nonce 0)
// Victim proxy: 0x51fF48f2d43966bE796692BdDdfaE96A435242a8 (unverified)
//
// Root cause (reproducible contract mechanism, verified against the on-chain trace, NOT a
// key/signer/privileged-claim compromise):
//   The attack contract exposes run(uint256,uint256,uint256), gated ONLY by a hardcoded
//   msg.sender == attacker EOA check (bytecode PUSH32 0xf8803dae..c7e; there is no admin role,
//   no signature, no owner-storage path). run() takes an Aave V3 flashLoanSimple of ARB from the
//   Aave V3 Pool 0x794a61358d6845594f94dc1db02a252b5b4814ad (selector 0x42b0b77c, asset ARB
//   0x912ce5..6548), and in the executeOperation callback it swaps against the Uniswap V3
//   ARB/USDC.e pool 0xcda53b1f66614552f834ceef361a8d12a0b8dad8 to skew that pool's spot price.
//   The Atomic strategy (0xf617a3ad1f0ab9d9fe39e48d688bfe44562769d9) and AtomicLending
//   (0xc1b677039892c048f2efb7e9c5da1b51fde92504) modules value the protocol's concentrated-
//   liquidity LP position / lending collateral off that same manipulated spot price, so under the
//   skew the attacker unwinds liquidity and withdraws more than was deposited. The extracted ARB
//   is routed ARB -> WETH -> USDC and the profit is forwarded to the attacker EOA at the end of
//   the same tx.
//     - log 1  : attack contract receives 18,485.478693 USDC.e from the manipulated pool 0xcda5..
//     - log 573: attack contract returns 18,485.478693 USDC.e to the pool (closing the position)
//     - log 579: attack contract receives 29,984.270865 native USDC from the final swap
//     - log 582: attack contract forwards 29,984.270865 native USDC to the attacker EOA
//   Every module function invoked is public and permissionless; the only "authorization" is the
//   manipulated on-chain price the modules trust. (Module/variable names are apparent-root-cause,
//   sourced from calldata + trace: the core vault/strategy/lending contracts are unverified.)
//
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-08/Atomic_exp.sol_
