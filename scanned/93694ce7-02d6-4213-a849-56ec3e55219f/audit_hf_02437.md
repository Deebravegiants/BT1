# [M] Suggested Governance-Restricted earn()

## Summary
Severity: Medium
Contest weight: 0.3989
Dataset id: 13083
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Stone protocol, a number of new strategy contracts have been designed and implemented to invest farmers assets (held in vaults), harvest growing yields, and sell any gains, if any, to the original asset. In order to have a smooth investment experience, the yVault contract opens up a public function, i.e., earn(), that can be invoked by anyone to kick off the investment.

```solidity
function earn() public {
    uint256 _bal = available();
    token.safeTransfer(controller, _bal);
    IController(controller).earn(address(token), _bal);
}
```

Unfortunately, this public entry has been exploited in a number of recent incidents (yDAI and BT hacks [18, 1]) that prompt the need of a guarded call to the earn(). By doing so, it ensures the assets in yVault will not blindly deposited into a faulty strategy that is currently not making any profit.

## Recommendation
Ensure the earn() can only be called via a trusted entity.
