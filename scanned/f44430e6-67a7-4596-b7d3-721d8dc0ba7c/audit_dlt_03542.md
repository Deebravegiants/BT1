# [H] Test configuration carryover to production deployment limits pool users to 5

## Summary
Severity: High
Chain: Smart contract
Component: 2021-06-pooltogether
Published: 2021-06-23
Source: https://github.com/code-423n4/2021-06-pooltogether-findings/issues/66
Type: code-finding

## Details
# Handle

0xRajeev


# Vulnerability details

## Impact

The project uses a data structure for indexing ticket tokens/users called SortitionSumTreeFactory which as explained in the overview video (time 14:20-14:50) is used to capture users’ token balances in the leaves where internal nodes represent their sums. However, the MAX_TREE_LEAVES constant is initialized to only 5, which seems like a testing configuration.

Impact: A production deployment with this configuration will limit pool users to only 5 which is not practical and will force contract redeployment upon discovery.

## Proof of Concept

Video walk-through (time 14:20-14:50): https://www.youtube.com/watch?v=YW4z5IvO1-E

https://github.com/code-423n4/2021-06-pooltogether/blob/85f8d044e7e46b7a3c64465dcd5dffa9d70e4a3e/contracts/Ticket.sol#L14

https://github.com/code-423n4/2021-06-pooltogether/blob/85f8d044e7e46b7a3c64465dcd5dffa9d70e4a3e/contracts/Ticket.sol#L36


## Tools Used

Manual Analysis

## Recommended Mitigation Steps

Change constant's value to production setting. Take care not to accidentally migrate testing configurations to production code. Consider having different environments for production and testing, with different contracts.
