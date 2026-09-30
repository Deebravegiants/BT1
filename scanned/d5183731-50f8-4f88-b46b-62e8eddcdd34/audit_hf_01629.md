# [M] Add max length bound to user's LRT deposits array

## Summary
Severity: Medium
Contest weight: 0.1761
Dataset id: 8754
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
getUserLoanInfo iterates over all user deposits to calculate the value of deposited LRTs. The maximum length of LRTs would be the number of LRTs configured in the CvToken contract. Additionally, the value of the RsEth LRT is calculated using the RsEthProtocol protocol. The getUnderlyingValue function is used to determine the value of a given amount of RsEth tokens. However, the RsEth deposit pool supports multiple LST tokens. Currently, to determine the RsEth value, getUnderlyingValue iterates over all supported LSTs to retrieve their asset balances. Since there is no maximum limit on the number of supported LSTs in the RsEth protocol, this number may increase in the future. Due to these two unbounded loops, there could be scenarios in the future where getUserLoanInfo reverts. For example, if a user has deposited multiple LRTs, including RsEth, and the number of supported LSTs for RsEth and deposited LRTs is sufficiently large, the transaction could exceed the block gas limit, causing it to revert. Although the likelihood of this happening is low, if it does occur, the user would be unable to withdraw all their deposits. Core functions such as liquidation and repayment would also fail, while only deposits would continue to work, increasing potential losses for the user.

## Recommendation
Limit the maximum number of LRTs a user can deposit.
