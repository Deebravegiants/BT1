# [M] setIncentiveSettings would be halt during a

## Summary
Severity: Medium
Contest weight: 0.4607
Dataset id: 20058
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
setIncentiveSettings would be halt during a rebalance operation that gets stuck due to supply cap is reached at Aave
rebalance implement a cap of tradeSize and if the need to rebalance require taking more assets than the maxTradeSize, then twapLeverageRatio would be set to the targeted leverage. twapLeverageRatio == 0 is required during rebalance.
Consider:
lever is needed during rebalance, the strategy require to borrow more ETH and sell to wstETH during the 1st call of rebalance the protocol cache the new twapLeverageRatio However wstETH market in Aave reach supply cap.
rebalance/iterateRebalance comes to a halt. twapLeverageRatio remains caching the targeted leverage
setIncentiveSettings requires a condition in which no rebalance is in progress. With the above case, setIncentiveSettings can be halted for an extended period of time until the wstETH market falls under supply cap.
Worth-noting, at the time of writing this issue, the wstETH market at Aave has been at supply cap
In this case, malicious actor who already has a position wstETH can do the following:
• deposit into the setToken, trigger a rebalance.
• malicious trader withdraw his/her position in Aave wstETH market so there opens up vacancy for supply again.
• protocol owner see supply vacancy, call rebalance in order to lever as required. Now twapLeverageRatio is set to new value since multiple trades are
• malicious trader now re-supply the wstETH market at Aave so it reaches supply cap again.
• the protocol gets stuck with a non-zero twapLeverageRatio, setIncentiveSettings can not be called.
```solidity
function setIncentiveSettings(IncentiveSettings memory _newIncentiveSettings)
external onlyOperator noRebalanceInProgress {
    incentive = _newIncentiveSettings;
    _validateNonExchangeSettings(methodology, execution, incentive);
    emit IncentiveSettingsUpdated(
        incentive.etherReward,
        incentive.incentivizedLeverageRatio,
        incentive.incentivizedSlippageTolerance,
        incentive.incentivizedTwapCooldownPeriod
    );
}
```
setIncentiveSettings would be halt.

## Recommendation
Add some checks on whether the supply cap of an Aave market is reached during a rebalance. If so, allows a re-set of twapLeverageRatio
