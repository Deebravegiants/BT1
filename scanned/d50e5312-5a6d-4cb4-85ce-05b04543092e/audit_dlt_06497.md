# [M] LM_PC_KPIRewarder_v1.sol#assertionResolvedCallback() - `LM_PC_KPIRewarder_v1` can be set as a callback address to another assertion in order to set `assertionPending = false`

## Summary
Severity: Medium
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-07
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/65
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** @EgisSec
**Submission hash (on-chain):** 0xd4cfef8c5c2062bdf82d352cef245fa5fd0c49e0532838c0ef40d57dba1ca425
**Severity:** medium

**Description:**
**Description**\
`assertionResolvedCallback` is a necessary function that the contract implements in order to integrate correctly with OOv3.

```sol
function assertionResolvedCallback(
        bytes32 assertionId,
        bool assertedTruthfully
    ) public override {
        // First, we perform checks and state management on the parent function.
        super.assertionResolvedCallback(assertionId, assertedTruthfully);

        // If the assertion was true, we calculate the rewards and distribute them.
        if (assertedTruthfully) {
            // SECURITY NOTE: this will add the value, but provides no guarantee that the fundingmanager actually holds those funds.

            // Calculate rewardamount from assertionId value
            KPI memory resolvedKPI =
                registryOfKPIs[assertionConfig[assertionId].KpiToUse];
            uint rewardAmount;

            for (uint i; i < resolvedKPI.numOfTranches; i++) {
                if (
                    resolvedKPI.trancheValues[i]
                        <= assertionConfig[assertionId].assertedValue
                ) {
                    // the asserted value is above tranche end
                    rewardAmount += resolvedKPI.trancheRewards[i];
                } else {
                    // tranche was not completed
                    if (resolvedKPI.continuous) {
                        // continuous distribution
                        uint trancheRewardValue = resolvedKPI.trancheRewards[i];
                        uint trancheStart =
                            i == 0 ? 0 : resolvedKPI.trancheValues[i - 1];

                        uint achievedReward = assertionConfig[assertionId]
                            .assertedValue - trancheStart;
                        uint trancheEnd =
                            resolvedKPI.trancheValues[i] - trancheStart;

                        rewardAmount +=
                            achievedReward * (trancheRewardValue / trancheEnd); // since the trancheRewardValue will be a very big number.
                    }
                    // else -> no reward

                    // exit the loop
                    break;
                }
            }

            _setRewards(rewardAmount, 1);
            assertionConfig[assertionId].distributed = true;
        } else {
            // To keep in line with the upstream contract. If the assertion was false, we delete the corresponding assertionConfig from storage.
            delete assertionConfig[assertionId];
        }

        // Independently of the fact that the assertion resolved true or not, new assertions can now be posted.
        assertionPending = false;
    }
```

You'll notice the last line, `assertionPending = false` and the comment above it.

>   // Independently of the fact that the assertion resolved true or not, new assertions can now be posted

`assertionPending` was added in response to [this issue from the previous report](https://docs.google.com/document/d/19joDIsfGkIHVBDrdY5GOb9r2wbYv1w2hBDFUTVHF6MM/edit#heading=h.ry4twwd87992). You can see that the recommendation is to not allow for more than 1 active assertion at a time, otherwise queued stakers can receive rewards for pending assertions. You can read the linked issue to get a better understanding, as the end result of this attack will be the same.

The issue here is that `assertionResolvedCallback` never checks if `assertionId` exists, meaning `assertionId` can be anything, which allows for anyone to use the address of `LM_PC_KPIRewarder_v1` as the `callbackRecipient` of another assertion that wasn't created by `LM_PC_KPIReawrder_v1`.

In the bellow section I'll explain how this will work.

**Attack Scenario**\
I'll be quoting several functions from OOv3, which can be found [here](https://github.com/UMAprotocol/protocol/blob/6ef5fe9d2fa5545c079603f8cd20f976aeb23295/packages/core/contracts/optimistic-oracle-v3/implementation/OptimisticOracleV3.sol)

1. The orchestrator admin `createKPI`, users `stake` and someone calls `postAssertion`. At this point `assertionPending = true`, which means no more assertions can be created from the contract, as if `postAssertion` is called it will fail on this line:
```sol
function postAssertion(
        bytes32 dataId,
        uint assertedValue,
        address asserter,
        uint targetKPI
    ) public onlyModuleRole(ASSERTER_ROLE) returns (bytes32 assertionId) {
        if (assertionPending) {
            revert Module__LM_PC_KPIRewarder_v1__UnresolvedAssertionExists();
        }
```
2. A malicious user creates his own assertion directly through OOv3 and sets the `callbackRecipient` to the address of `LM_PC_KPIRewarder_v1` and sets `escalationManagerSettings.discardOracle = false` so when he settles the assertion, `_callbackOnAssertionResolve` will be called.
3. He `disputeAssertion` on his own assertion and then calls `settleAssertion`when he knows that `settlementResolution = false`, meaning that the assertion wasn't asserted truthfuly.
4. `_callbackOnAssertionResolve` is called, which will call `assertionResolvedCallback` on the `LM_PC_KPIRewarder_v1`.
5. `assertionResolvedCallback` is called with an `assertionId` that doesn't exist for the `LM_PC_KPIRewarder_v1`, but that's never checked. Also `assertedTruthfully = false`, so we enter the else statement:
```sol
else {
            // To keep in line with the upstream contract. If the assertion was false, we delete the corresponding assertionConfig from storage.
            delete assertionConfig[assertionId];
        }
```
6. Because this is a mapping, this will delete an empty `assertionConfig` and won't revert.
7. Then we hit the final line of the function, which will set `assertionPending = false`.

At this point another real assertion can be created with `postAssertion`, which will be a problem when the first one gets resolved as [explained in the issue mentioned above](https://docs.google.com/document/d/19joDIsfGkIHVBDrdY5GOb9r2wbYv1w2hBDFUTVHF6MM/edit#heading=h.ry4twwd87992)

**Attachments**

1. **Proof of Concept (PoC) File**

2. **Revised Code File (Optional)**

Check that `assertionId` actually exists and then continue resolving the assertion.
