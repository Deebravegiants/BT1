# [M] Incorrect key usage in transfer delay feature causes global sell swap restriction

## Summary
Severity: Medium
Contest weight: 0.1579
Dataset id: 4220
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The transferDelayEnabled function is designed to enforce a delay between consecutive token transfers to prevent rapid trading and potential market manipulation. This feature is particularly relevant during the initial trading period, where it enforces a 10-block delay between sell transactions to automated market maker (AMM) pairs. However, there is an issue in the implementation of this feature within the _transfer function. The key used to track the last transfer timestamp in the _holderLastTransferTimestamp mapping is msg.sender, which is typically the address of the Uniswap router during swaps. This results in the transfer delay being applied globally to all users, rather than individually. Consequently, during the first 20 minutes of trading, only one sell swap can be performed every ten blocks across the entire user base, severely restricting trading activity.

## Recommendation
To resolve this issue, the key used in the _holderLastTransferTimestamp mapping should be changed from msg.sender to from. This adjustment ensures that the transfer delay is applied on a per-user basis, rather than globally. By using the from address as the key, the contract will correctly track the last transfer timestamp for each individual user, allowing the intended 10-block delay to be enforced for each user's sell transactions to AMM pairs. If the 10-blocks delay is intended to be enforced only between sell swaps, the update of _holderLastTransferTimestamp should be moved inside the if (_automatedMarketMakerPairs[to]) branch.
