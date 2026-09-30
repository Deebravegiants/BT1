# [M] Revisited withdrawSubscriptions() Logic in SubscriptionFacet

## Summary
Severity: Medium
Contest weight: 0.4164
Dataset id: 13455
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
xRaise has a SubscriptionFacet feature that allows to add/update/remove user subscriptions. While reviewing the related subscription-removing logic, we notice the implementation should be revisited. To elaborate, we show below the implementation of the related withdrawSubscriptions() routine. This routine is defined public and can be called by anyone to withdraw active subscriptions. For each active subscription, it may only be called once in one subscription period. However, the subscription token should be sent to the subscription.to, not msg.sender.
```solidity
function withdrawSubscriptions() public {
    for (uint256 i = 0; i < subscriptionStorage().subscriptionIds.length; i++) {
        SubscriptionInfo storage subscription = subscriptionStorage().subscriptions[
            subscriptionStorage().subscriptionIds[i]
        ];
        if (subscription.isActive && !subscription.isDeleted && block.timestamp >= subscription.nextChargeTime) {
            IERC20(subscription.token).transfer(msg.sender, subscription.price);
            subscription.nextChargeTime = block.timestamp + subscriptionPeriodToTime(subscription.period);
        }
    }
}
```

## Recommendation
Revise the above logic to properly handle subscription withdrawal.
