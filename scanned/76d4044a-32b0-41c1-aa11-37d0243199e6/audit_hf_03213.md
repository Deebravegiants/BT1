# [M] resolveQueuedTrades() ERC777 re-enter to

## Summary
Severity: Medium
Contest weight: 0.5650
Dataset id: 17815
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
_openQueuedTrade() does not follow the “Checks Effects Interactions” principle and may lead to re-entry to steal the funds
https://fravoll.github.io/solidity-patterns/checks_effects_interactions.html
The prerequisite is that tokenX is ERC777 e.g. “sushi”
1. resolveQueuedTrades() call _openQueuedTrade()
2. in _openQueuedTrade() call "tokenX.transfer(queuedTrade.user)" if (revisedFee < queuedTrade.totalFee) before set queuedTrade.isQueued = false;
```solidity
function _openQueuedTrade(uint256 queueId, uint256 price) internal {
    ...
    if (revisedFee < queuedTrade.totalFee) {
        IERC20 tokenX = IERC20(optionsContract.tokenX());
        tokenX.transfer(
            queuedTrade.user,
            queuedTrade.totalFee - revisedFee
        );
    }
    queuedTrade.isQueued = false;
    // change state
}
```
3. if ERC777 re-enter to #cancelQueuedTrade() to get tokenX back, it can close, because queuedTrade.isQueued still equal true
4. back to _openQueuedTrade() set queuedTrade.isQueued = false
5. so steal tokenX
if tokenX equal ERC777 can steal token

## Recommendation
follow “Checks Effects Interactions”
```solidity
function _openQueuedTrade(uint256 queueId, uint256 price) internal {
    ...
    queuedTrade.isQueued = false;
    // Transfer the fee to the target options contract
    IERC20 tokenX = IERC20(optionsContract.tokenX());
    tokenX.transfer(queuedTrade.targetContract, revisedFee);
    emit OpenTrade(queuedTrade.user, queueId, optionId);
}
```
