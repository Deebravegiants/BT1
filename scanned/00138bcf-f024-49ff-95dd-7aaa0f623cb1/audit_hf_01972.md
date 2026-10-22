# [M] Missing Pausability Check in OstiumTrading::executeAutomationOrder() for Opening Orders

## Summary
Severity: Medium
Contest weight: 0.3577
Dataset id: 11133
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of an absent pause guard in the function that processes automated limit orders. When the contract is placed in a paused state – typically to halt trading during emergencies or upgrades – most entry points verify the pause flag before performing state‑changing actions. In this case the executeAutomationOrder routine, which is responsible for opening limit orders, does not check whether the contract is paused. The root cause is a missing require statement or Pausable modifier that would reject calls while the pause flag is true. An attacker or any user can invoke executeAutomationOrder while the contract is paused, causing new limit orders to be opened or existing ones to be executed despite the intended suspension of trading. This can lead to unexpected order fills, mismatched accounting, and potential loss of funds for traders who assume that no trades occur during a pause. The impact is most visible to users who place limit orders; they may see orders being filled when the UI indicates trading is halted, balances changing without consent, or refunds not being processed as expected. The condition occurs only when the contract is paused, which is a state that should block all order‑related functions. The issue was discovered during a manual audit that compared the pause checks across the contract’s public functions and identified the omission. Because the function is internal and may be called through automation scripts, the lack of a pause guard can be subtle and may not surface in normal testing unless the pause state is explicitly exercised. To remediate, the function should include a pause verification, either by adding a require(!paused) statement at the start of executeAutomationOrder or by applying the standard Pausable modifier to the function. Additionally, the logic that validates the existence of an open limit order should be retained, ensuring that only legitimate orders are processed. By enforcing the pause check, the contract will honor the emergency stop mechanism, preventing order execution when trading is intended to be disabled and preserving the integrity of user balances and protocol accounting.

## Recommendation
```solidity
if (orderType == IOstiumTradingStorage.LimitOrder.OPEN) {
if (!storageT.hasOpenLimitOrder(trader, pairIndex, index)) {
```
