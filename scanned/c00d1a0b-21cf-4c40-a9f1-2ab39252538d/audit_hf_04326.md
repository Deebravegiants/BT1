# [M] M-01 | Lacking Initial Tick Validation May Brick The Protocol

## Summary
Severity: Medium
Contest weight: 0.1171
Dataset id: 21482
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The BPOOL module is initialized with the starting values for activeTick and floorTick. The current validation only checks that activeTick > floorTick. At this moment, checkpointTick is also initialized with the same value as activeTick. The issue rises when initial activeTick value is not greater than floorTick + TS, as the active tick will be at the FLOOR range, ANCHOR range won't exist, and DISCOVERY range will be initialized with 0 liquidity. Additionally, if this initial setup is created, then no marketMaking operations can be executed, even if the price start trading upwards: • bump - checkpoint is at the FLOOR • sweep - Panic reverts when calculating liquidityPremium as liquidityA is 0 • slide - activeTick is above checkpoint

## Recommendation
Replace the tick values validation in the initializePool with: require(_initialFloorTick + TS < _initialActiveTick, "Invalid tick values");
