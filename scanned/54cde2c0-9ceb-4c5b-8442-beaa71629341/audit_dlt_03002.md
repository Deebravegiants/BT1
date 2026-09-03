# [?] UnistreetLaunchpad - Arbitrary call injection via unvalidated launch forwarding

## Summary
Severity: Unknown
Chain: Ethereum
Component: UnistreetLaunchpad
Published: 2026-08-06
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-08/UnistreetLaunchpad_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$17,743.91 USDC + ~0.0072 WETH (plus 9 illiquid launch memecoin positions)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

// unistreetsx launchpad — Uniswap-V4 LP-custody drain via unvalidated launch() calldata forwarding
// ~$17.75K netted by the attacker EOA in a single CONTRACT-CREATION transaction.
//
// Exploit tx : 0x9583e95d5c88c7966e269197f4b09022f26b7a27ad2c13660dda6774e3136d14 (block 25692311)
//   The tx has NO `to` field: it is a raw CONTRACT-CREATION. The EOA deploys the attack
//   contract 0xc7d8c70f4349AcC55409800C8768e801b7556B77, whose CONSTRUCTOR runs the entire
//   exploit and forwards the proceeds back to the EOA in the same tx. There is no second call,
//   no separate withdraw tx.
//
// Root cause (reproducible contract mechanism, NOT a key/signer/privileged-claim compromise):
//   LaunchpadFactoryAuto.launch() (0xfb60cd...825) forwards attacker-supplied init/modify
//   calldata VERBATIM into Uniswap V4 PositionManager.multicall(), with the factory itself as
//   msg.sender, with no validation on the calldata content. The factory custodies EVERY launch's
//   Uniswap V4 LP-position NFT as custodian. The attacker:
//     1. calls the PUBLIC launch() to create its own throwaway launch token "CPOC"
//        (0x3d8a2f...988e), which mints 1,000,000 CPOC to the factory and opens its LP position,
//     2. inside that same launch() passes modifyCalldata = setApprovalForAll(exploitContract, true)
//        (selector 0xa22cb465), which the factory forwards to the V4 PositionManager
//        (0xbd216513...ee9e) AS ITSELF, granting the attacker approval over ALL LP-position NFTs
//        the factory holds (posm ApprovalForAll event, log index 4),
//     3. the constructor then burns each launch LP position the factory custodies via
//        posm.modifyLiquidities() + a TAKE_PAIR action (example tokenId 360162, "UNISTREET"),
//        sweeping the underlying tokens out of the V4 PoolManager (0x0000...04444c5dc75...) to
//        the attack contract,
//     4. forwards every swept token to tx.origin (the attacker EOA) before the constructor returns.
//   Every step is a permissionless PUBLIC function (launch, multicall, modifyLiquidities) driven
//   entirely by attacker-crafted calldata. No owner key, no admin role, no privileged upgrade,
//   no signature. Confirmed against the on-chain trace: the tx is sent from a plain EOA (nonce 6)
//   with an empty `to`, and the only "authorization" the factory checks — its own custody of the
//   NFTs — is exactly what the injected setApprovalForAll subverts.
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-08/UnistreetLaunchpad_exp.sol_
