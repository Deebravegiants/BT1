# [M] 5.1 Preferential Withdrawal

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Risk Accepted

When there are more withdrawal requests than can be serviced, all users receive the same percentage
of their withdrawals. A user that wants to make a partial withdrawal could take advantage of this.

Consider an example where withdrawal requests are fulfilled at 50%. A user that wants to withdraw 100
shares could instead request to withdraw 200 shares (given he has enough shares). Their request would
be fulfilled by half, giving them 100 shares. Now they can cancel the remaining withdrawal request.

In this way, the user was able to circumvent the withdrawal limit at no cost. Other users were able to
withdraw fewer shares than they would have otherwise.

Risk accepted:

Avantgarde Finance states:

```
This is the intended behavior. Also note that redeemers who request to redeem more
than they actually would like to redeem are risking that their entire requested
amount be redeemed in full if the cap is not met, the cap is updated by the manager,
or other redeemers cancel their requests.
```
