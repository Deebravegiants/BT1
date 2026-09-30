# [M] _distribute() function in RFPSimpleStrategy

## Summary
Severity: Medium
Contest weight: 0.6761
Dataset id: 20467
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function _distribute():
```solidity
function _distribute(address[] memory, bytes memory, address _sender)
    internal
    virtual
    override
    onlyInactivePool
    onlyPoolManager(_sender)
{
    IAllo.Pool memory pool = allo.getPool(poolId);
    Milestone storage milestone = milestones[upcomingMilestone];
    Recipient memory recipient = _recipients[acceptedRecipientId];
    if (recipient.proposalBid > poolAmount) revert NOT_ENOUGH_FUNDS();
    uint256 amount = (recipient.proposalBid * milestone.amountPercentage) / 1e18;
    poolAmount -= amount;//<@@ NOTICE the poolAmount get decrease over time
    _transferAmount(pool.token, recipient.recipientAddress, amount);
    ...
}
```
Let's suppose this scenario:
• Pool manager funding the contract with 100 token, making poolAmount variable equal to 100
• Pool manager set 5 equal milestones with 20% each
• Selected recipient's proposal bid is 100, making recipients[acceptedRecipientId].proposalBid variable equal to 100
• After milestone 1 done, pool manager pays recipient using distribute(). Value of variables after: poolAmount = 80, recipients[acceptedRecipientId].proposalBid = 100
• After milestone 2 done, pool manager will get DOS trying to pay recipient using distribute() because of this line:
if (recipient.proposalBid > poolAmount) revert NOT_ENOUGH_FUNDS();
This behaviour will cause DOS when distributing the 2nd milestone or higher

## Recommendation
```solidity
if (recipient.proposalBid > poolAmount) revert NOT_ENOUGH_FUNDS();
```
```solidity
if ((recipient.proposalBid * milestone.amountPercentage) / 1e18 > poolAmount) revert NOT_ENOUGH_FUNDS();
```
