# [H] insufficient_update_window_validation_can_cause_denial_of_service_in_forceupdatenodes

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23453
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The AvalancheL1Middleware constructor fails to validate that the UPDATE_WINDOW parameter is less than the EPOCH_DURATION. This validation is critically important because the onlyDuringFinalWindowOfEpoch modifier, which is essential for stake management functionality, will permanently revert if UPDATE_WINDOW is greater than or equal to EPOCH_DURATION.

The onlyDuringFinalWindowOfEpoch modifier works by enforcing that a function can only be called during a specific time window at the end of an epoch:
```solidity
modifier onlyDuringFinalWindowOfEpoch() {
    uint48 currentEpoch = getCurrentEpoch();
    uint48 epochStartTs = getEpochStartTs(currentEpoch);
    uint48 timeNow = Time.timestamp();
    uint48 epochUpdatePeriod = epochStartTs + UPDATE_WINDOW;
    if (timeNow < epochUpdatePeriod || timeNow > epochStartTs + EPOCH_DURATION) { //@audit always
        // reverts if UPDATE_WINDOW >= EPOCH_DURATION,!
        revert AvalancheL1Middleware__NotEpochUpdatePeriod(timeNow, epochUpdatePeriod);
    }
    _;
}
```
The modifier creates a valid execution window only when:
- timeNow >= epochStartTs + UPDATE_WINDOW (after the update window starts)
- timeNow <= epochStartTs + EPOCH_DURATION (before the epoch ends)

For this window to exist, UPDATE_WINDOW must be less than EPOCH_DURATION.

The constructor currently only validates that slashingWindow is not less than epochDuration but lacks a check for the UPDATE_WINDOW:
```solidity
constructor(
    AvalancheL1MiddlewareSettings memory settings,
    // other parameters...
) AssetClassRegistry(owner) {
    // other checks...
    if (settings.slashingWindow < settings.epochDuration) {
        revert AvalancheL1Middleware__SlashingWindowTooShort(
            settings.slashingWindow,
            settings.epochDuration
        );,!
    }
    // @audit No validation for UPDATE_WINDOW relation to EPOCH_DURATION
    // Initializations...
    EPOCH_DURATION = settings.epochDuration;
    UPDATE_WINDOW = settings.stakeUpdateWindow;
    // other initializations...
}
```
Since both EPOCH_DURATION and UPDATE_WINDOW are set as immutable variables, this issue cannot be corrected after deployment.

Impact: The forceUpdateNodes() function will be permanently unusable since it's protected by the onlyDuringFinalWindowOfEpoch modifier.

## Recommendation
Consider adding an explicit validation in the constructor to ensure that `UPDATE_WINDOW > 0 && UPDATE_WINDOW < EPOCH_DURATION`. Additionally, consider adding a comment clearly explaining the relationship between these time parameters to help prevent configuration errors:
```solidity
/**
 * @notice Required relationship between time parameters:
 * 0 < UPDATE_WINDOW < EPOCH_DURATION <= SLASHING_WINDOW
 */
```
