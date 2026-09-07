# [?] Aztec Connect - numRealTxs Proof/Settlement Mismatch (permissionless RollupProcessorV3)

## Summary
Severity: Unknown
Chain: Ethereum
Component: AztecConnect
Published: 2026-06-14
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/AztecConnect_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$2.19M (this PoC reproduces the 908.99 ETH leg)

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";

// @KeyInfo - Total Lost : ~$2.19M (908.99 ETH + 270.5K DAI + 167.9 wstETH + yvDAI/yvWETH/LUSD/yvLUSD)
//                          This PoC covers the 908.99 ETH leg.
// Attacker EOA          : 0x0F18D8b44a740272f0be4d08338d2b165b7EdD17 (funded via Tornado Cash)
// Attacker Orchestrator : 0x06f585F74e0DA633Ae813A0f23Fb9900B61d0fcD (4-byte trigger 0x6f3ce701)
// Vulnerable contract   : 0xFF1F2B4ADb9dF6FC8eAFecDcbF96A2B351680455 (Aztec Connect RollupProcessorV3, deprecated)
// Attack Tx             : 0x074ec9317d8336db37e8c348fbdd7515573ff4088239c77ab429f522509aeeb1 (block 25,315,715)
//
// @Analysis
// Attack date : Jun-14-2026
// Chain       : Ethereum mainnet
// Post-mortem : https://www.cryptotimes.io/2026/06/15/aztec-exploit-drains-2-19m-from-dormant-privacy-protocol/
// Foundation  : https://x.com/aztecFND/status/2066175938887619055
//
// @Root cause - numRealTxs mismatch between proof/hash coverage and L1 settlement (core/Decoder.sol):
//
//   * decodeProof() commits the public inputs in FULL inner-rollup chunks. With numRealTxs = 1,
//     rollupSize = 1024 and numRollupTxs = 32 (innerSize = 1024/32 = 32), it hashes ceil(1/32) = 1
//     full chunk -> ALL 32 slots of inner-rollup #0 are proven and their notes minted into L2 state.
//
//   * processDepositsAndWithdrawals() settles EXACTLY numRealTxs txs:  end = ptr + numRealTxs * 256.
//     With numRealTxs = 1 only slot 0 is settled.
//
//   => A DEPOSIT placed in slot 1 is proven (note minted) but its L1 validation
//      (decreasePendingDepositBalance + shield signature) is SKIPPED -> unbacked L2 balance,
//      later withdrawn for real ETH. The proof is a normal, valid rollup proof; nothing is forged.
//      On the deprecated RollupProcessorV3, processRollup() is permissionless (the provider gate was
//      removed for sunset self-exit), so anyone can submit these rollups.
//
//   numRealTxs lives at proofData[0x11c0], OUTSIDE the 0..0x11c0 header that is hashed, so it is NOT
//   bound by the zk proof. It only sets the chunk COUNT ceil(numRealTxs/32), and 1..32 all map to one
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/AztecConnect_exp.sol_
