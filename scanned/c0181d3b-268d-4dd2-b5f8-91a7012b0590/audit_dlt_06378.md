# [M] An attacker can DoS `enterFarm`

## Summary
Severity: Medium
Chain: Smart contract
Component: Wise-Lending
Published: 2024-02-17
Source: https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/issues/42
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** @00xSEV
**Submission hash (on-chain):** 0x314d38b19d7ccf83ae5e52e84222ed81050f6f37c5aea7d022893d81d53cf270
**Severity:** medium

**Description:**
**Description**\
Anyone can deposit on the NFTs that have not yet been minted.  
The NFT ID is determined as, roughly speaking, [lastId + 1](https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/blob/23e90440820fce1b355b771df0e82d4564b7fcab/contracts/PositionNFTs.sol#L105).  
`enterFarm` calls [`_getWiseLendingNFT`](https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/blob/23e90440820fce1b355b771df0e82d4564b7fcab/contracts/PowerFarms/PendlePowerFarm/PendlePowerManager.sol#L107), which calls `_registrationFarm`, which in turn calls `WISE_LENDING.setRegistrationIsolationPool`, which calls `_validateZero(WISE_SECURITY.overallETHCollateralsBare(_nftId))`. It will revert if there is any collateral on the NFT.

Furthermore, anyone can call [`reservePositionForUser`](https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/blob/23e90440820fce1b355b771df0e82d4564b7fcab/contracts/PositionNFTs.sol#L70) to assign a specific NFT to a user.

**Attack Scenario**: 
1. Attacker reserves NFTs for some users, deposit some dust and locks `enterFarm` for them
2. Attacker deposits on future NFTs and lock `enterFarm` for any new user

**Impact**:
`enterFarm` will revert
It can also lead to unexpected calculation errors because the code may not anticipate the deposited amount on newly minted NFTs.

**Attachments**:
in contracts/Tests

```solidity
// SPDX-License-Identifier: -- WISE --

pragma solidity =0.8.24;

import "forge-std/Test.sol";
import "forge-std/StdUtils.sol";
import "./WisenLendingShutdown.t.sol";
import { PendlePowerFarmControllerBaseTest } from "./PendlePowerFarmControllerBase.t.sol";

import "../PositionNFTs.sol";
import "../Tests/TesterLending.t.sol";
import "../WiseSecurity/WiseSecurity.sol";
import { PendlePowerManager } from "../PowerFarms/PendlePowerFarm/PendlePowerManager.sol";
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/issues/42_
