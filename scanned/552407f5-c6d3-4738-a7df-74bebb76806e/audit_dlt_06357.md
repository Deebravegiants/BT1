# [M] Incorrect Allocation results in `getQuestAllocationForPeriod` when `questRewardToken` has Decimals other than 18

## Summary
Severity: Medium
Chain: Smart contract
Component: Paladin
Published: 2024-02-11
Source: https://github.com/hats-finance/Paladin-0x1610bfde27e57b068af7f38aec3d2a7b1d146989/issues/37
Type: hats-finding

## Details
**Github username:** @chainNue
**Twitter username:** chainNue
**Submission hash (on-chain):** 0xc24d2916bc90d76389dce246dac38acc72f5be3dfcd458783a75eb858ad13273
**Severity:** medium

**Description:**
**Description**

In Distributor contract, `questBoard` can `addQuest` with prefered `questId` and a reward token.
Looking on several sources, this reward token could be a USDC [0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48](https://etherscan.io/token/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48):

- on Quest create [page](https://quest.paladin.vote/#/create), there is option to choose USDC as reward token
- on deployed [QuestBoard](https://etherscan.io/address/0xF13e938d7a1214ae438761941BC0C651405e68A4#readContract), the USDC is one of whitelisted reward token

The USDC token is using 6 decimals, unlike DAI 18 decimals.

```js
File: MultiMerkleDistributorV2.sol
291:     function addQuest(uint256 questID, address token) external returns(bool) {
...
296:         // Add a new Quest using the QuestID, and list the reward token for that Quest
297:         questRewardToken[questID] = token;
298:
299:         if(!rewardTokens[token]) rewardTokens[token] = true;
...
304:     }
```

When `updateQuestPeriod` is executed, `notifyDistributedQuestPeriod` on `LootCreator` will be called passing the `totalAmount` which is the `questRewardsPerPeriod`, (6 decimals)

On `LootCreator` this amount will be saved into `totalQuestPeriodRewards`. Next when calculating allocation (Line 411), it will passed as `questTotalRewards`.

Here, in `_getQuestAllocationForPeriod`, the calculation will face a conversion issue, since the UNIT conversion is 1e18 and not considering the reward decimal.

```js
File: LootCreator.sol
403:     function _getQuestAllocationForPeriod(
404:         address gauge,
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Paladin-0x1610bfde27e57b068af7f38aec3d2a7b1d146989/issues/37_
