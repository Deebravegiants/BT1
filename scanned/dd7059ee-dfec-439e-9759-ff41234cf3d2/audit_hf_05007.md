# [M] Staking Deepr tokens does not retain votes in

## Summary
Severity: Medium
Contest weight: 0.4274
Dataset id: 22996
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Staking Deepr tokens does not retain votes in the Governance protocol. According to https://www.deepr.finance/staking and https://medium.com/@Deepr.Finance/unlock-passive-earnings-staking-deepr-with-deepr-finance-a3d932473afd, the token staked using the deepr-staking-contract/contracts/RewardPool.sol is the Deepr token. An important attribute of the Deepr token is its voting ability in the Governance protocol. Naturally, a governance token should maintain its voting capability to the contract. Currently, if a user owns Deepr tokens and stakes them, the delegated votes simply disappears, because delegates[] for the RewardPool is empty.

```solidity
function _transferTokens(address src, address dst, uint96 amount) internal {
    require(src != address(0), "Comp::_transferTokens: cannot transfer from the zero address");
    require(dst != address(0), "Comp::_transferTokens: cannot transfer to the zero address");
    balances[src] = sub96(balances[src], amount, "Comp::_transferTokens: transfer amount exceeds balance");
    balances[dst] = add96(balances[dst], amount, "Comp::_transferTokens: transfer amount overflows");
    emit Transfer(src, dst, amount);
    _moveDelegates(delegates[src], delegates[dst], amount);
}
```
If a user owns Deepr tokens and stakes them, the delegated votes simply disappears.

## Recommendation
Two ways for mitigation:
1. When the Deepr token transfer is to/from the RewardPool address, skip transferring votes. This way the votes would retain to the users. can receive the votes.
