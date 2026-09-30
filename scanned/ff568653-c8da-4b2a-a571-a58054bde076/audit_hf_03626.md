# [M] Risk with Liquidation

## Summary
Severity: Medium
Contest weight: 0.4059
Dataset id: 19694
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Due to the approval system with pvGLP, liquidations may be less likely
In times of intense price action, a liquidation may have to be performed on pvGLP.
The protocol will offer liquidate which will sweep funds out, this is fine and will work as intended because it relies on transferFrom.
However, a liquidator will receive the vault token, and may be unable to redeem it.
That's because redemptions have to be performed via plvGLP depositor which may not have approved the liquidators account.
This will make it less likely for liquidators to perform the operation as it may force either a manual operation (redemption can be performed by any EOA), or it will require further setup, reducing the number of operators willing to perform the liquidation in the time of need.
```solidity
function _isEligibleSender() private view {
    if (
        msg.sender != tx.origin && whitelist.isWhitelisted(msg.sender) == false &&
        partners[msg.sender].isActive == false
    ) revert UNAUTHORIZED();
}
```

## Recommendation
No recommendation available
