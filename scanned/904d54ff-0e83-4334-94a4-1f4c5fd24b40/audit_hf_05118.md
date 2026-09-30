# [M] Not decreasing oracle timestamp validation causes DoS

## Summary
Severity: Medium
Contest weight: 0.1784
Dataset id: 23161
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol only allows equal or increased timestamp of oracle prices whenever an action happens in the protocol. This validation is wrong since it will lead to DoS for users.
The protocol uses RedStone oracle, where token prices are added as a part of calldata of transactions. In RedStone oracle, it allows prices from 3 minutes old upto 1 minute in the
In oracle.vy, it extracts the token price from the RedStone payload, which also includes the timestamp of which the prices were generated. As shown in the code snippet, the protocol reverts when the timestamp extracted from the calldata is smaller than the stored timestamp, thus forcing timestamps only increase or equal to previous one. This means that the users who execute transaction with price 1 minute old gets reverted when there is another transaction executed with price 30 seconds old.
considerable delays based on the location, api availability, etc.
By abusing this vulnerability, an attacker can regularly make transactions with newest prices which will revert all other transactions with slightly older price data like 10-20 seconds older, can be all reverted.
The vulnerability causes DoS for users who execute transactions with slightly older RedStone oracle data.

## Recommendation
It's recommended to remove that non-decreasing timestamp validation. If the protocol wants more strict oracle price validation than the RedStone does, it can just use the difference between oracle timestamp and current timestamp.
