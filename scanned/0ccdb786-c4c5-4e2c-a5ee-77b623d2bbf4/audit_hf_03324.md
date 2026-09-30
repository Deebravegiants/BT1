# [M] ORDH-2 | Frozen Orders Cannot Be Simulated

## Summary
Severity: Medium
Contest weight: 0.0479
Dataset id: 18175
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability concerns the inability to simulate a frozen order in a trading contract. When an order is placed, the system provides a simulation function that checks whether the order would be valid under current market conditions. This simulation is gated by an internal authentication routine called _validateFrozenOrderKeeper, which only permits callers that are recognised as frozen order keepers. If an order becomes frozen – for example because it was manually paused, flagged by risk controls, or otherwise put into a non‑executable state – the normal user (the order owner or a front‑end service) is no longer recognised as a frozen order keeper. Consequently, any attempt to call the simulation endpoint reverts with an authorization error, preventing the caller from obtaining a validity check. The root cause is the overly restrictive access control that ties the simulation path to a role that is unavailable once the order is frozen. An attacker who can trigger the freezing mechanism can therefore deny legitimate users the ability to simulate their own orders, creating a denial‑of‑service condition. Users attempting to simulate a frozen order will see a transaction failure or an error message indicating that msg.sender is not authorized, leading to confusion and the perception that the order is stuck or that funds are lost. Because the simulation is often used by front‑ends to display expected outcomes, the failure can hide critical information about whether the order can be rescued, cancelled, or will eventually execute, potentially resulting in funds remaining locked indefinitely. The issue was discovered during a systematic audit when the test suite attempted to simulate a frozen order and the call reverted. It is subtle because the simulation works correctly for active orders, so the problem only appears under the specific frozen state, which may not be covered by standard unit tests. To remediate, the simulation function should either bypass the _validateFrozenOrderKeeper check or be refactored so that the role restriction does not apply when the purpose is merely to read or validate order state. This change would restore the ability for any caller, including the order owner, to simulate frozen orders, ensuring that users can still assess order status, plan withdrawals, or take corrective actions, thereby preserving the expected accounting guarantees of the protocol.

## Proof of Concept
https://github.com/GuardianAudits/GMX_3/blob/main/test/Guardian/PoCs/ORDH-2.ts

## Recommendation
Allow the simulation to bypass the _validateFrozenOrderKeeper authentication check.
