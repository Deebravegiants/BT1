# [H] Improper confirmDispute() Logic in SmartBridge

## Summary
Severity: High
Contest weight: 0.5966
Dataset id: 12079
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned earlier, the SmartBridge provides a unique dispute mechanism so that a user may attempt to raise a dispute. The dispute, once confirmed, allows the user to recover the deposit. While examining the mechanism to confirm a dispute, we notice an issue that may prevent the user from recovering the deposit. To elaborate, we show below the related routine, i.e., confirmDispute(). We notice that the confirmation should be performed at most twice from two different authorized entities. However, the related enforcement should be performed as require(dispute[disputeID].confirms < 2), not current require(dispute[disputeID].confirms <= 2 (line 568). As mentioned earlier, an incorrect enforcement may block the user from claiming back the previous deposit.
```solidity
function confirmDispute(uint256 disputeID, bool _bool) external nonReentrant {
    require(admin[msg.sender], "not admin");
    require(dispute[disputeID].confirms <= 2, "already 2");
    require(!dispute[disputeID].refunded, "already");
    require(block.timestamp <= deposit[dispute[disputeID].depositID].expireTime, "expired");
    require(!confirmed[msg.sender][disputeID], "already disputed");
    confirmed[msg.sender][disputeID] = true;
    dispute[disputeID].confirms += 1;
    if (_bool) {
        dispute[disputeID].closed = true;
    }
    // Public
```

## Recommendation
Revisit the above routine to properly conform the dispute.
