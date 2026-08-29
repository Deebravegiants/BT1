# [?] New Market Trading - SquidRouterModule Missing Caller Check

## Summary
Severity: Unknown
Chain: Ethereum
Component: NewMarketTrading
Published: 2026-05-25
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-05/NewMarketTrading_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$3.98M USD

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "../interface.sol";

// @KeyInfo - Total Lost : ~$3.98M USD across 88 Gnosis Safes on Ethereum / Base / Arbitrum
//                         (this PoC drains one Ethereum victim Safe: ~5,806 USDC)
// Attacker      : 0x7c82cB4b2909C50C7c0F2B696Eee7565e0a23BB8 (main operator)
//                 0x9BDC730183821b6bb2B51BE30B77C964FA645b91 (co-operator, sent this tx)
// Attack Contract : 0xe1d5FCfBba4d46F4937de369De415dD7E2D3265a (Ethereum wrapper)
// Vulnerable Contract : 0x1f1d37a3Bf840e35c6a860c7C2dA71Fe555123ca (New Market Trading "SquidRouterModule" Safe module)
// Victim Safe   : 0xa081B9F72d586624F2eaA1eaCf53C1A268810e4E
// Attack Tx     : 0x59d17fd31e31959b2d562508bf91c4fc1271682ba7d61a6209865e1151b69aea
// @Analysis
// Attack date: May 25, 2026  Chain: Ethereum  Block: 25170513
// rekt.news: https://rekt.news/newmarkettrading-rekt
// Verified source (same address, Base): https://base.blockscout.com/address/0x1f1d37a3Bf840e35c6a860c7C2dA71Fe555123ca?tab=contract
//
// Run (Cancun EVM is required -- the Uniswap UniversalRouter uses EIP-1153 transient storage;
//      the repo default evm_version is 'shanghai'):
//   FOUNDRY_EVM_VERSION=cancun forge test --contracts src/test/2026-05/NewMarketTrading_exp.sol \
//       --match-contract NewMarketTradingExploit -vv
//
// Root Cause:
// The SquidRouterModule is a Gnosis Safe module that lets a whitelisted Squid/Axelar bridge message run
// swap/approve actions on a Safe. It inherits Axelar's AxelarExpressExecutableWithToken, which exposes:
//
//   function expressExecuteWithToken(bytes32 commandId, string sourceChain, string sourceAddress,
//                                    bytes payload, string symbol, uint256 amount) external payable {
//       ...
//       IERC20(gatewayToken).safeTransferFrom(msg.sender, address(this), amount); // relayer fronts `amount`
//       _executeWithToken(commandId, sourceChain, sourceAddress, payload, symbol, amount);
//   }
//
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-05/NewMarketTrading_exp.sol_
