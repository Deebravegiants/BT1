# [?] OneInchFusionV1SettlementHack exploit (2025-03)

## Summary
Severity: Unknown
Chain: Ethereum
Component: OneInchFusionV1SettlementHack
Published: 2025-03
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-03/OneInchFusionV1SettlementHack.sol_exp.sol
Type: defi-exploit-poc

## Details
References:
- https://blog.1inch.io/fusion-swap-resolving-the-offchain-component/
- https://blog.1inch.io/fusion-mode-swap-resolving-45a9203f95e9/

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.15;

import "../basetest.sol";
import "./../interface.sol";



// @KeyInfo - Total Lost : 4.5M
// Attacker : https://etherscan.io/address/0xA7264a43A57Ca17012148c46AdBc15a5F951766e
// Attack Contract : https://etherscan.io/address/0x019BfC71D43c3492926D4A9a6C781F36706970C9
// Vulnerable Contract : https://etherscan.io/address/0xa88800cd213da5ae406ce248380802bd53b47647
// Funds Receiver: https://etherscan.io/address/0xbbb587e59251d219a7a05ce989ec1969c01522c0
// Attack Tx : https://etherscan.io/tx/0x62734ce80311e64630a009dd101a967ea0a9c012fabbfce8eac90f0f4ca090d6

// @Info
// Vulnerable Contract Code : https://etherscan.io/address/0xa88800cd213da5ae406ce248380802bd53b47647#code

// @Analysis
// Twitter Guy : https://x.com/DecurityHQ/status/1898069385199153610
// Post-mortem : https://blog.decurity.io/yul-calldata-corruption-1inch-postmortem-a7ea7a53bfd9

// @Relevant Repos
// How it works: https://web.archive.org/web/20230422045124/https://blog.1inch.io/fusion-swap-resolving-onchain-component/
//               https://blog.1inch.io/fusion-swap-resolving-the-offchain-component/
//               https://blog.1inch.io/fusion-mode-swap-resolving-45a9203f95e9/
// Settlement: https://github.com/1inch/fusion-protocol/blob/934a8e7db4b98258c4c734566e8fcbc15b818ab5/contracts/Settlement.sol
// Audit Limit: https://blog.openzeppelin.com/1inch-limit-order-protocol-audit
// Dedaub of Attacker contract: https://app.dedaub.com/ethereum/address/0x019bfc71d43c3492926d4a9a6c781f36706970c9/decompiled

// Attacker contract is not very important for this hack
// as it mostly relays the orders to the settlement contract
// it acts as a maker/taker for the orders
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-03/OneInchFusionV1SettlementHack.sol_exp.sol_
