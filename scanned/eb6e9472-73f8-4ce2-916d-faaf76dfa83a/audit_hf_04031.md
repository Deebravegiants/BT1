# [M] QVBaseStrategy::reviewRecipients() doesn't

## Summary
Severity: Medium
Contest weight: 0.5931
Dataset id: 20458
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the QV strategy contracts, recipients register themselves and wait for a pool manager to accept the registration. Pool managers can accept or reject recipients with the reviewRecipients() function. There is also a threshold (reviewThreshold) for recipients to be accepted. For example, if the reviewThreshold is 2, a pending recipient gets accepted when two managers accept this recipient and the recipientStatus is updated.
However, QVBaseStrategy::reviewRecipients() function doesn't check the recipient's current status. This one alone may not be an issue because managers may want to change the status of the recipient etc.
But on top of that, the function also doesn't take the previous review counts into account when updating the status, and overwrites the status immediately after reaching the threshold. I'll share a scenario later about this below.
Here is the reviewRecipients() function:
https://github.com/allo-protocol/allo-v2/blob/main/allo-v2/contracts/strategies/qv-base/QVBaseStrategy.sol#L254C1-L288C6
file: QVBaseStrategy.sol
```solidity
function reviewRecipients(address[] calldata _recipientIds, Status[] calldata _recipientStatuses)
    external
    virtual
    onlyPoolManager(msg.sender)
    onlyActiveRegistration
{
    // make sure the arrays are the same length
    uint256 recipientLength = _recipientIds.length;
    if (recipientLength != _recipientStatuses.length) revert INVALID();
    for (uint256 i; i < recipientLength;) {
        Status recipientStatus = _recipientStatuses[i];
        address recipientId = _recipientIds[i];
        // if the status is none or appealed then revert
        if (recipientStatus == Status.None || recipientStatus == Status.Appealed) {
            revert RECIPIENT_ERROR(recipientId);
        }
        reviewsByStatus[recipientId][recipientStatus]++;
        if (reviewsByStatus[recipientId][recipientStatus] >= reviewThreshold) {
            Recipient storage recipient = recipients[recipientId];
            recipient.recipientStatus = recipientStatus;
            emit RecipientStatusUpdated(recipientId, recipientStatus, address(0));
        }
        emit Reviewed(recipientId, recipientStatus, msg.sender);
        unchecked {
            ++i;
        }
    }
}
```
As I mentioned above, the function updates the recipientStatus immediately after reaching the threshold. Here is a scenario of why this might be an issue.
Example Scenario
The pool has 5 managers and the reviewThreshold is 2.
1. The first manager rejects the recipient
2. The second manager accepts the recipient
3. The third manager rejects the recipient. -> recipientStatus updated -> status = REJECTED
4. The fourth manager rejects the recipient -> status still REJECTED
5. The last manager accepts the recipient ->recipientStatus updated again -> status = ACCEPTED
3 managers rejected and 2 managers accepted the recipient but the recipient status is overwritten without checking the recipient's previous status and is ACCEPTED now.
Coded PoC
You can prove the scenario above with the PoC. You can use the protocol's own setup for this.
- Copy the snippet below and paste it into the QVBaseStrategy.t.sol test file.
- Run forge test --match-test test_reviewRecipient_reviewTreshold_OverwriteTheLastOne
```solidity
function test_reviewRecipient_reviewTreshold_OverwriteTheLastOne() public virtual {
    address recipientId = __register_recipient();
    // Create rejection status
    address[] memory recipientIds = new address[](1);
    recipientIds[0] = recipientId;
    IStrategy.Status[] memory Statuses = new IStrategy.Status[](1);
    Statuses[0] = IStrategy.Status.Rejected;
    // Reject three times with different managers
    vm.startPrank(pool_manager1());
    qvStrategy().reviewRecipients(recipientIds, Statuses);
    vm.startPrank(pool_manager2());
    qvStrategy().reviewRecipients(recipientIds, Statuses);
    vm.startPrank(pool_manager3());
    qvStrategy().reviewRecipients(recipientIds, Statuses);
    // Three managers rejected. Status will be rejected.
    assertEq(uint8(qvStrategy().getRecipientStatus(recipientId)), uint8(IStrategy.Status.Rejected));
    assertEq(qvStrategy().reviewsByStatus(recipientId, IStrategy.Status.Rejected), 3);
    // Accept two times after three rejections
    Statuses[0] = IStrategy.Status.Accepted;
    vm.startPrank(pool_admin());
    qvStrategy().reviewRecipients(recipientIds, Statuses);
    vm.startPrank(pool_manager4());
    qvStrategy().reviewRecipients(recipientIds, Statuses);
    // 3 Rejected, 2 Accepted, but status is Accepted because it overwrites right after passing threshold.
    assertEq(uint8(qvStrategy().getRecipientStatus(recipientId)), uint8(IStrategy.Status.Accepted));
    assertEq(qvStrategy().reviewsByStatus(recipientId, IStrategy.Status.Rejected), 3);
    assertEq(qvStrategy().reviewsByStatus(recipientId, IStrategy.Status.Accepted), 2);
}
```
You can find the test results below:
Running 1 test for test/foundry/strategies/QVSimpleStrategy.t.sol:QVSimpleStrategyTest
[PASS] test_reviewRecipient_reviewTreshold_OverwriteTheLastOne() (gas: 249604)
Test result: ok. 1 passed; 0 failed; 0 skipped; finished in 10.92ms
Recipient status might be overwritten with less review counts.
https://github.com/allo-protocol/allo-v2/blob/main/allo-v2/contracts/strategies/qv-base/QVBaseStrategy.sol#L254C1-L288C6
file: QVBaseStrategy.sol
```solidity
function reviewRecipients(address[] calldata _recipientIds, Status[] calldata _recipientStatuses)
    external
    virtual
    onlyPoolManager(msg.sender)
    onlyActiveRegistration
{
    // make sure the arrays are the same length
    uint256 recipientLength = _recipientIds.length;
    if (recipientLength != _recipientStatuses.length) revert INVALID();
    for (uint256 i; i < recipientLength;) {
        Status recipientStatus = _recipientStatuses[i];
        address recipientId = _recipientIds[i];
        // if the status is none or appealed then revert
        if (recipientStatus == Status.None || recipientStatus == Status.Appealed) {
            revert RECIPIENT_ERROR(recipientId);
        }
        reviewsByStatus[recipientId][recipientStatus]++;
        if (reviewsByStatus[recipientId][recipientStatus] >= reviewThreshold) {
            Recipient storage recipient = recipients[recipientId];
            recipient.recipientStatus = recipientStatus;
            emit RecipientStatusUpdated(recipientId, recipientStatus, address(0));
        }
        emit Reviewed(recipientId, recipientStatus, msg.sender);
        unchecked {
            ++i;
        }
    }
}
```

## Recommendation
Checking the review counts before updating the state might be helpful to mitigate this issue
