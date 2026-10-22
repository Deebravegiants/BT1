# [H] DSPC.set can bypass the cfg.step constraint by including the same id multiple times in the updates array and continuously increase the bps

## Summary
Severity: High
Contest weight: 0.2235
Dataset id: 5468
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The DSPC.set function allows a bud (whitelisted actor) to modify the rates for SSR, DSR, or any collateral stability fee. A ward can restrict this action by defining min, max, and step parameters for the individual rates.
The step parameter specifies the maximum value by which a rate can be increased in a single call.
// Calculates absolute difference between the old and the new rate
uint256 delta = bps > oldBps ? bps - oldBps : oldBps - bps;
require(delta <= cfg.step, "DSPC/delta-above-step");
The next set call should be only possible after a freeze period defined by tau. However, a bud can bypass the cfg.step constraint by including the same id multiple times in the updates array and continuously increase the bps.
Each loop iteration updates the rate, and the subsequent iteration incorrectly interprets it as the old rate.
This would allow to set the rate to the maximum in one single call.

## Recommendation
The set function could enforce the updates array to be sorted, which would easily detect duplicates in the updates array.
