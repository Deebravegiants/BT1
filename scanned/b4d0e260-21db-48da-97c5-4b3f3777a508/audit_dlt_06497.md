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
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/65_
