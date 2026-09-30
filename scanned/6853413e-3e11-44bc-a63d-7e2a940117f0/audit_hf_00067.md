# [M] OCL-3 | Impossible to Close Option

## Summary
Severity: Medium
Contest weight: 0.1060
Dataset id: 143
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During the expiration of an option, it should be finalized using the settleOptionsExpired function. Within this function, the getSpotPriceAtTime method is invoked, which contains an unbounded loop. If this loop runs for an extended period, it can exhaust more gas than what's permissible in a single transaction, rendering the option impossible to close. The loop's duration is determined by the number of rounds that transpire between the option's expiration and the invocation of settleOptionsExpired. For tokens with high volatility, the number of rounds can escalate rapidly, potentially leading to a Denial of Service (DoS) situation sooner than anticipated.

## Recommendation
Closely monitor the closing of options and ensure the function is called with adequate time before a DoS is possible.
