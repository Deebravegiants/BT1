# [?] LegendaryMoneyMonNft - ecrecover address(0) Signature Bypass

## Summary
Severity: Unknown
Chain: BNB Chain
Component: LegendaryMoneyMonNft
Published: 2026-05-28
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-05/LegendaryMoneyMonNft_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$85.5K USD (85,519 USDT)

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "../interface.sol";

// @KeyInfo - Total Lost : ~$85.5K USD (85,519.47 USDT)
// Attacker : 0xE1582248C593Df4B367e131922438Fec9D76E787
// Attack Contract : 0x157ba211f05dd2c83006be949e12b2f0f0a0c1d9 (delegated to the attacker EOA via EIP-7702)
// Vulnerable Contract : 0x92D60629FF5d53a0098B51E9b1D59546D1D8e5B6 (LegendaryMoneyMonNft - "Legendary MoneyMon NFTs")
// MON Token : 0xA1C1A7341a1713F174D59926E49E4A1228924100 (Moneymon / MON)
// Attack Tx : 0x15c835c070672948b3487d35254bce96831bec9f5212f78b04e683fed74bf4a2
// @Analysis
// Attack date: May 28, 2026
// Chain: BSC, Block: 100937039
// SlowMist: https://x.com/SlowMist_Team/status/2060205558687486441

// Root Cause:
// LegendaryMoneyMonNft.cliamRewred() lets a user pull an arbitrary ERC20 amount out of the contract
// as long as verify() returns true:
//
//   function verify(address payment,address user,uint _nftid,uint amount,uint _time,string _exname,bytes sig)
//       returns (bool) { ... return recoverSigner(ethSignedMessageHash, sig) == admin; }
//
//   function recoverSigner(bytes32 hash, bytes sig) returns (address) {
//       (bytes32 r, bytes32 s, uint8 v) = splitSignature(sig);
//       return ecrecover(hash, v, r, s);          // <-- never checks for the address(0) return
//   }
//
// `ecrecover` returns address(0) for a malformed signature (e.g. r = s = 0). The contract never rejects
// that, and `changeadmin()` had already been used to set `admin` to the zero address on-chain. So an
// attacker submits cliamRewred(...) with a 65-byte signature of (r=0, s=0, v=27): ecrecover returns
// address(0), which equals admin, verify() passes, and the contract transfers the requested token amount
// to msg.sender. The attacker drains the contract's entire MON balance and swaps it to USDT on PancakeSwap.
//
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-05/LegendaryMoneyMonNft_exp.sol_
