# [M] This protocol doesn't support all fee on transfer tokens

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-11-streaming
Published: 2021-12-06
Source: https://github.com/code-423n4/2021-11-streaming-findings/issues/192
Type: code-finding

## Details
# Handle

0x0x0x


# Vulnerability details

Some fee on transfer tokens, do not reduce the fee directly from the transferred amount, but subtracts it from remaining balance of sender. Some tokens prefer this approach, to make the amount received by the recipient an exact amount. Therefore, after funds are send to users, balance becomes less than it should be. So this contract does not fully support fee on transfer tokens. With such tokens, user funds can get lost after transfers.

## Mitigation step

I don't recommend directly claiming to support fee on transfer tokens. Current contract only supports them, if they reduce the fee from the transfer amount.
