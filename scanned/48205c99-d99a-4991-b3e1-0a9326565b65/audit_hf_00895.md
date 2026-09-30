# [M] Vault.settle(account=coordinator) will lose

## Summary
Severity: Medium
Contest weight: 0.6935
Dataset id: 2652
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Vault.settle() turns a portion of the profit into profitShares for coordinator. Use method _credit() to save profitShares to storage. But it doesn't update the memory variable context.local.shares. It doesn't take into account the case where account == coordinator. This way, if you maliciously specify that the settlement account is coordinator, settle() will end up overwriting the new value with the old value in memory. Resulting in loss of profitShares.
/Vault.sol#L390 settle() call _credit()
```solidity
function _settle(Context memory context, address account) private {
    ...
    while (
        context.global.current > context.global.latest &&
        context.latestTimestamp >= (nextCheckpoint = _checkpoints[context.global.latest + 1].read()).timestamp
    ) {
        // process checkpoint
        (context.mark, profitShares) = nextCheckpoint.complete(
            context.mark,
            context.parameter,
            _checkpointAtId(context, nextCheckpoint.timestamp)
        );
        context.global.shares = context.global.shares.add(profitShares);
        _credit(coordinator, profitShares);
```
in Vault.sol#L424 save to storage but don't update context.local.shares
```solidity
        Account memory local = _accounts[account].read();
        local.shares = local.shares.add(shares);
        _accounts[account].store(local);
    }
```
but at the last _saveContext() save context.local.shares to storage, it will override _credit() value if account == coordinator
```solidity
function _saveContext(Context memory context, address account) private {
    if (account != address(0)) _accounts[account].store(context.local);
    _accounts[address(0)].store(context.global);
    _checkpoints[context.currentId].store(context.currentCheckpoint);
    mark = context.mark;
}
```
Internal Pre-conditions
External Pre-conditions
Attack Path
Example context[coordinator].local.shares = 0
1. anyone call settle(account = coordinator)
2. suppose profitShares = 10
3. in _credit() save storage _accounts[coordinator].shares = profitShares = 10, but context.local.shares still 0
4. at last _saveContext() will overwrite _accounts[coordinator].shares = context.local.shares = 0
5. coordinator lose 10 shares
coordinator lose profitShares

## Recommendation
like Market.sol#_credit(), if coordinator == context.account, only change context.local.shares
```solidity
internal virtual {
    if (account == context.account)
        context.local.shares = context.local.shares.add(shares)
    else {
        Account memory local = _accounts[account].read();
        local.shares = local.shares.add(shares);
        _accounts[account].store(local);
    }
}
```
