# [M] `userQuestPeriodRewards` will be overwritten on second claim

## Summary
Severity: Medium
Chain: Smart contract
Component: Paladin
Published: 2024-02-10
Source: https://github.com/hats-finance/Paladin-0x1610bfde27e57b068af7f38aec3d2a7b1d146989/issues/29
Type: hats-finding

## Details
**Github username:** @chainNue
**Twitter username:** chainNue
**Submission hash (on-chain):** 0x1df5f76bc7c7a49a9c7e5c537fc43c8e4a498bd9220b3dd2658ea6476ec87943
**Severity:** medium

**Description:**
**Description**

Claim in Distributor is based by `index` (not just by `account` address), thus, it's possible for a user (address) to have a second claim on the same `questId` and `period`.

For example, when `emergencyUpdateQuestPeriod` happen, `MerkleRoot` will be updated for adjustment. The adjustment might contains additional claim for some users.

According to comment, `for all new claims to be added, set them after the last index of the previous Merkle Tree`, when this new claim includes user who already claimed (or not), then they will have 2 indexes of claim.

When this user did their first claim, the `_triggerCreateLoot` is called which then call `LootCreator`'s `notifyQuestClaim`, which will set `userQuestPeriodRewards` for corresponding distributor, questId, period, and user.

```js
File: MultiMerkleDistributorV2.sol
148:     function claim(uint256 questID, uint256 period, uint256 index, address account, uint256 amount, bytes32[] calldata merkleProof) public nonReentrant {
...
164:         _triggerCreateLoot(account, questID, period, amount);
165: 
166:         emit Claimed(questID, period, index, amount, rewardToken, account);
167:     }

File: LootCreator.sol
275:     function notifyQuestClaim(address user, uint256 questId, uint256 period, uint256 claimedAmount) external onlyAllowedDistributor nonReentrant {
276:         userQuestPeriodRewards[msg.sender][questId][period][user] = claimedAmount;
277:     }
```

The problem here is on his second claim. When he claim on the second time, the `notifyQuestClaim` will be called again, but now, it will overwrite the `userQuestPeriodRewards`, as it's an assignment (`=`), not an incremental (`+=`). Thus, the first claim value will be overwritten by the second claim, which is not what expected. User will get less `userQuestPeriodRewards` than they should have.

**Attack Scenario**

**Attachments**

1. **Proof of Concept (PoC) File**

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Paladin-0x1610bfde27e57b068af7f38aec3d2a7b1d146989/issues/29_
