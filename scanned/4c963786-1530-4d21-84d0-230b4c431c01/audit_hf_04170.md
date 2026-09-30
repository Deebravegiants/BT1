# [H] H-04 | Lacking Gas Yields Claiming Logic

## Summary
Severity: High
Contest weight: 0.1295
Dataset id: 20851
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There are several contracts in the Abracadabra and Mimswap systems that cannot claim gas yields as they accrue. These contracts include: MIM FeeRateModel and FeeRateImplementation BlastTokenRegistry SPELL Some of these contracts will accrue a large amount of gas yields, for instance MIM will accrue gas yields upon every transfer, approval etc… and the FeeRateModel and FeeRateImplementation will accrue gas yields on every swap in the Mimswap system.

## Recommendation
Consider implementing gas yield claiming logic for these contracts.
