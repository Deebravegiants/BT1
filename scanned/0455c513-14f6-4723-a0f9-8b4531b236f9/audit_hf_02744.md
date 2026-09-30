# [M] Do collect() First In GClaimManager

## Summary
Severity: Medium
Contest weight: 0.3961
Dataset id: 15034
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Situation:
The function join() of GClaimManager.sol pulls target to backfill for previous collect()s. However, if collect() hasn’t been called for a long time (or not called at all), the user might not have enough target for the backfill.
```solidity
function join(address adapter, uint48 maturity, uint256 uBal) external {
    ...
    /* Pull the amount of `Target` needed to
    backfill the `excess` back to issuance,
    retrieves previously `collect()`'ed `target`
    */
    ERC20(Adapter(adapter).target()).safeTransferFrom(msg.sender, address(this), tBal);
    ...
    // Pull Collect Claims to GClaimManager.sol
    ERC20(claim).safeTransferFrom(msg.sender, address(this), uBal);
    /* This will call `Divider.collect()`
    and send target to the `msg.sender` */
    ...
}
```

## Recommendation
If the Sense Team agrees this is an issue, then call Divider.collect() at the beginning of function join().
