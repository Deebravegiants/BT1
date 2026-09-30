# [C] C-01 | Claims By The Collector Prevented

## Summary
Severity: Critical
Contest weight: 0.2118
Dataset id: 1998
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _getClaimChecksFromVestingConfigs function the checks.collectors array is assigned a length based on the numCollectors which is purely the number of conﬁgs which satisfy c.collector = address(0). However the criteria for an address to be added to the checks.collectors array is isForCollector & co.collector = msg.sender. Therefore the checks.collectors array will have empty entries for the conﬁgs that are claimed by the collector address themselves. The checks.collectors array with empty entries is then used to verify the claim with the ClaimChecker contract on L1. The _checkCollectorClaim(claimer, collectors[i]) check will trivially fail because no claimer can be approved in the delegate registry for the zero address. Therefore these claims cannot be veriﬁed and cannot be completed.

## Recommendation
Shrink the length of the checks.collectors array after writing to it or adjust the way the numCollectors is calculated so that it is only incremented in the case where isForCollector && c.collector = msg.sender.
