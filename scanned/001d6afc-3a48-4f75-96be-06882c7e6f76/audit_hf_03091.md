# [M] Interchanged function arguments

## Summary
Severity: Medium
Contest weight: 0.1086
Dataset id: 17465
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The positions of arguments totalPoolValue and exchangeParams.spotPrice in the function call _getLiquidity are accidentally interchanged compared to what is expected by the parameters of _getLiquidity. The first two arguments of _getLiquidity within _getTokenPriceAndStale are interchanged. Instead of: _getLiquidity(exchangeParams.spotPrice, totalPoolValue,...) _getLiquidity(totalPoolValue, exchangeParams.spotPrice,...) This will break the liquidityThresholdCrossed constraint in the circuit-breaker _updateCBs and would cause a DoS with the protocol unable to make progress because CBTimestamp check in _canProcess will always fail while processing deposit/withdrawal queues. This would then require the guardian to take over and

## Recommendation
No recommendation available
