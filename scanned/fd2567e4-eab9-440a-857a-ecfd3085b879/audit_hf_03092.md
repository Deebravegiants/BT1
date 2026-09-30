# [M] Accurate price at board expiry is not ensured

## Summary
Severity: Medium
Contest weight: 0.1333
Dataset id: 17466
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The expiration date for a board can be set by settleExpiredBoard function. It queries the spot price from the Synthetix contracts and sets the boardToPriceAtExpiry assuming the price is close to the expiration time. There is no on-chain mechanism take on the responsibility of calling the function at board expiration and that they will implement a mechanism to incentivize users (i.e. keepers) to call the function. If no one calls settleExpiredBoard function at board expiration and it’s only later called after a longer period has been passed, then it is possible that the current spot price deviates significantly from the one at board expiration. The settlement of the expired board could lead to financial loss for some users.

## Recommendation
It is recommended to implement an on-chain mechanism that ensures that the boardToPriceAtExpiry is always accurate and as close to the expiration time as possible. Keepers will be run to ensure this function is called as soon as possible after expiry. This feature can be added in the future, there is no simple way to get this data on-chain. In the case of an outage, there most likely will not be a chainlink feed that can be read from to get accurate data. Sounds reasonable.
