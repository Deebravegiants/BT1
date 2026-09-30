# [C] \[C01\] Trapped Proposer Reward

## Summary
Severity: Critical
Source: https://github.com/UMAprotocol/protocol/blob/d4e7ea22159b2eed8e39d5b86ce0026ea3b8b995/packages/core/contracts/financial-templates/long-short-pair/LongShortPair.sol#L369-L372
Type: audit-issue

## Details
The `LongShortPair` contract [retrieves a proposer reward](https://github.com/UMAprotocol/protocol/blob/d4e7ea22159b2eed8e39d5b86ce0026ea3b8b995/packages/core/contracts/financial-templates/long-short-pair/LongShortPair.sol#L369-L372) from whichever address triggers the expiration, which is used to incentivize price proposals in the Optimistic Oracle. However, the `LongShortPairCreator` contract also [retrieves and forwards the funds](https://github.com/UMAprotocol/protocol/blob/d4e7ea22159b2eed8e39d5b86ce0026ea3b8b995/packages/core/contracts/financial-templates/long-short-pair/LongShortPairCreator.sol#L112-L113) from the deployer address. These additional funds are not passed to the Optimistic Oracle, and instead remain trapped within the `LongShortPair` contract.

Consider removing the duplicate transfer.

**Update:** _Fixed as of commit [9bab1ff353a417952ba8c96a098773f340d9da17](https://github.com/UMAprotocol/protocol/pull/3523/commits/9bab1ff353a417952ba8c96a098773f340d9da17) in [PR3523](https://github.com/UMAprotocol/protocol/pull/3523)._
