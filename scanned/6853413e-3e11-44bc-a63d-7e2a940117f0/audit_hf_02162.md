# [M] Incorrect raiseDispute() Logic in SmartBridge

## Summary
Severity: Medium
Contest weight: 0.4438
Dataset id: 12078
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The SmartBridge provides users the ability to cross-bridge transfer. It also enables the unique dispute mechanism so that a user may attempt to raise a dispute which, once confirmed, allows the user to recover the deposit. While examining the mechanism to raise a dispute, we notice an issue in current implementation. To elaborate, we show below the related raiseDispute() routine. As the name indicates, this routine is used to raise a dispute. Upon the entry, this routien makes a number of validations. And we notice the very first validation checks whether the given depositID has been refunded. However, the check is performed as require(!dispute[depositID].refunded), which should be revised as require(!deposit[depositID].refunded).
```solidity
function raiseDispute(uint256 depositID) external nonReentrant {
    require(!dispute[depositID].refunded, "already");
    require(!deposit[depositID].completed, "already Complete");
    require(block.timestamp <= deposit[depositID].expireTime, "expired");
    require(block.timestamp >= deposit[depositID].depositTime + 1 hours, "not mature");
    require(deposit[depositID].user == msg.sender, "not user");
    dispute.push();
    myDisputeIDs[msg.sender].push(dispute.length - 1);
    dispute[dispute.length - 1].user = deposit[depositID].user;
    dispute[dispute.length - 1].depositID = depositID;
    dispute[dispute.length - 1].toChain = deposit[depositID].toChainId;
    dispute[dispute.length - 1].amount = deposit[depositID].amount;
    // Set deposit disputeID
    deposit[depositID].disputeID = dispute.length - 1;
    openDisputes += 1;
    emit RaiseDispute(msg.sender, deposit[depositID].amount, depositID);
```

## Recommendation
Properly validate the given depositID is not refunded yet when a dispute is raised.
