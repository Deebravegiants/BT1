# [M] The oracle price could be tampered

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-02-gmx
Published: 2023-03-25
Source: https://github.com/sherlock-audit/2023-02-gmx-judging/issues/74
Type: sherlock-finding

## Details
KingNFT

high

# The oracle price could be tampered

## Summary
The ````_setPrices()```` function is missing to check duplicated prices indexes. Attackers such as malicious order keepers can exploit it to tamper signed prices.

## Vulnerability Detail
The following test script shows how it works
```typescript
import { expect } from "chai";

import { deployContract } from "../../utils/deploy";
import { deployFixture } from "../../utils/fixture";
import {
  TOKEN_ORACLE_TYPES,
  signPrices,
  getSignerInfo,
  getCompactedPrices,
  getCompactedPriceIndexes,
  getCompactedDecimals,
  getCompactedOracleBlockNumbers,
  getCompactedOracleTimestamps,
} from "../../utils/oracle";
import { printGasUsage } from "../../utils/gas";
import { grantRole } from "../../utils/role";
import * as keys from "../../utils/keys";

describe("AttackOracle", () => {
  const { provider } = ethers;

  let user0, signer0, signer1, signer2, signer3, signer4, signer7, signer9;
  let roleStore, dataStore, eventEmitter, oracleStore, oracle, wnt, wbtc, usdc;
  let oracleSalt;

  beforeEach(async () => {
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2023-02-gmx-judging/issues/74_
