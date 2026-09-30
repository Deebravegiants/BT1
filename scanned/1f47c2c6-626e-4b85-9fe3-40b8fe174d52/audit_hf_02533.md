# [H] RedstoneChainlinkPriceOracle.valuation() can return outdated valuation and funds can be stolen from the index

## Summary
Severity: High
Contest weight: 0.1817
Dataset id: 13533
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The CalldataExtractor.extractTimestampsAndAssertAllAreEqual() function only checks the calldata format but not the legitimacy of the data or the timestamp. This means that if the oldest saved price in staticRedstoneData is say from 1 hour ago or even a week ago, an attacker can provide bytes calldata such that the outdated valuation is returned. An attacker can intentionally access the outdated valuation to deposit() into the Index and receive more shares than he is entitled to or redeem() from the Index and receive more constituents/reserve than he should be able to. This is a direct loss to the other users of the protocol.

## Recommendation
The else case in the RedstoneChainlinkPriceOracle.valuation() function needs to validate the staticRedstoneData.timestamp. If the timestamp is outdated, the function needs to revert and the outdated valuation can thus not be used.
