# [M] Revisited deposit() Logic in Mixer1

## Summary
Severity: Medium
Contest weight: 0.4378
Dataset id: 12537
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Mixer1 contract allows users to deposit supported assets and the deposit will be charged for 1% fee. Our analysis shows the current deposit logic needs to be revised. To elaborate, we show below the related deposit() routine. Notice that it allows the deposit more than the speciﬁed LIMIT and the user is limited to withdraw LIMIT - ParticipationFee. Moreover, it comes to our attention that the deposit logic makes a low-level call to the contract itself, i.e., payable(address(this)).call() (line 61) and this low-level call is always reverted. The reason is that the contact does not implement the receive() or fallback() handlers to accept the native coin. With that, we suggest to remove this speciﬁc low-level call and refund the user if the user sends extra tokens (msg.value-LIMIT).
```solidity
function deposit(uint256 identityCommitment) public payable {
    if (LIMIT > msg.value) {
        revert("Insufficient inventory");
    }
    if (CommitmentState[identityCommitment] == true) {
        revert("It is used Commitment");
    }
    // calculate fee
    uint ParticipationFee = LIMIT * FEE / 10000;
    uint Total = LIMIT - ParticipationFee;
    (bool success,) = payable(address(this)).call{value: Total}("");
    (bool succesd,) = payable(LAYAER).call{value: ParticipationFee}("");
    verifiyer.addMember(IndexId, identityCommitment);
    CommitmentState[identityCommitment] = true;
    CommitmentList.push(identityCommitment);
    WithAble[identityCommitment] = Total;
    emit Deposit(identityCommitment, block.timestamp);
}
```

## Recommendation
Revise the above routine to remove the low-level call as well as refund extra funds that have been sent in.
