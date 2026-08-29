# [H] `InvestToken`: Whitelisted investors can inflate USDE to infinity by arbitraging previous and current price differences

## Summary
Severity: High
Chain: Smart contract
Component: Euro-Dollar
Published: 2024-11-04
Source: https://github.com/hats-finance/Euro-Dollar-0xa4ccd3b6daa763f729ad59eae75f9cbff7baf2cd/issues/45
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** thekmj_
**Submission hash (on-chain):** 0x431f96317f2d6a268db53da199722aced8e43996eab6723a431d0a8906d2d2d9
**Severity:** high

**Description:**
**Description**\

`InvestToken` mimics an ERC4626 vault, where the USDE is the underlying asset, and the exchange rate is determined by the `YieldOracle`. The token also supports classic ERC4626 functions including `mint`, `redeem`, `deposit`, and `withdraw`. It is worth nothing that the exchange rate fetched from `YieldOracle` is forced to be uponly.

The mistake here is that `mint` and `redeem` uses `convertToAsset()`, which in turn calls into `YieldOracle.sharesToAssets()`, which uses `previousPrice` for conversion, however `deposit` and `withdraw` uses `YieldOracle.assetsToShares()`, which uses the current price.

This means that depositing through `mint` uses the previous (lower) price, whereas `withdraw` uses the current (higher) price, providing avenue for instant arbitraging.

**Attack Scenario**\

An investor is whitelisted for `InvestToken` and can exploit as follow:
- Assuming the previously commited price is 1.00, or 1 USDE per shares. The newest committed price is 1.01, or 1.01 USDE per shares, due to yield.
- The investor/exploiter converts 1 USDE into shares using `mint`. They are given 1 shares.
- The investor/exploiter immediately converts 1 share back into USDE using `withdraw`. However, they get back 1.01 USDE due to the conversion using the higher price.

The investor just minted 0.01 USDE for free. Now repeat for as long as they like, for however amount they like, and they have inflated USDE to infinity. Then simply sell it on the market and take profit before the admin can act.

**Attachments**

1. **Proof of Concept (PoC) File**

Run with `forge test --match-test testExploit`.

```solidity
pragma solidity ^0.8.21;

import {Test} from "forge-std/Test.sol";
import {ERC1967Proxy} from "@openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol";
import {Math} from "@openzeppelin/contracts/utils/math/Math.sol";
import {IUSDE} from "../src/interfaces/IUSDE.sol";
import {IYieldOracle} from "../src/interfaces/IYieldOracle.sol";
import {InvestToken} from "../src/InvestToken.sol";
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Euro-Dollar-0xa4ccd3b6daa763f729ad59eae75f9cbff7baf2cd/issues/45_
