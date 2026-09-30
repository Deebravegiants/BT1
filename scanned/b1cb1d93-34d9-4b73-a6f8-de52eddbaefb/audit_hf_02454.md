# [M] Possible MAXIMUM_COMMIT_ETH/WHALE_MAXIMUM_COMMIT_ETH Bypass

## Summary
Severity: Medium
Contest weight: 0.4622
Dataset id: 13159
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
DeFi protocols typically have a number of system-wide parameters that can be dynamically configured on demand. The WhitelistSbSale contract is no exception. Specifically, if we examine the WhitelistSbSale contract, it has defined a number of protocol-wide risk parameters, such as MAXIMUM_COMMIT_ETH and WHALE_MAXIMUM_COMMIT_ETH. These two parameters indicate the maximum commited ETHs that may be allowed in the IDO during the limit period. However, while examining the enforcement of these parameters, we notice they might be bypassed. In the following, we use the first parameter MAXIMUM_COMMIT_ETH as the example and show the related _addCommitment() routine that violates its enforcement. Notice this routine is invoked when a new commitment is being made. Suppose it is still in the limit period, and the new commitment, if successful, will make the following condition true: limitCommitPeriod() && _commitment.add(marketStatus.commitmentsTotal) > marketInfo.commitmentCap (line 266). In this case, the variable canCommitmentAmount computes the maximum allowed commit from the current user. However, it is currently computed as marketInfo.commitmentCap.sub(marketStatus.commitmentsTotal), which fails to consider earlier commitments that may be made by the same user. As a result, a user may commit multiple times to exceed the MAXIMUM_COMMIT_ETH cap.

```solidity
function _addCommitment(address payable _addr, uint256 _commitment, address _referral) private {
    require(block.timestamp >= marketInfo.startTime && block.timestamp <= marketInfo.endTime, "SbSale: outside presale hours");
    require(!marketStatus.finalized, "SbSale: has been finalized");
    if (limitCommitPeriod() && _commitment.add(marketStatus.commitmentsTotal) <= marketInfo.commitmentCap)
        require(commitments[_addr] < MAXIMUM_COMMIT_ETH, "SbSale: exceed maximum commit eth");
    if (commitments[_addr].add(_commitment) >= MAXIMUM_COMMIT_ETH) {
        uint256 _canCommitmentAmount = MAXIMUM_COMMIT_ETH.sub(commitments[_addr]);
        uint256 _refundAmount = _commitment.sub(_canCommitmentAmount);
        _commitment = _canCommitmentAmount;
        _safeTransferETH(_addr, _refundAmount);
    } else if (limitCommitPeriod() && _commitment.add(marketStatus.commitmentsTotal) > marketInfo.commitmentCap) {
        uint256 _canCommitmentAmount = marketInfo.commitmentCap.sub(marketStatus.commitmentsTotal);
        if (_canCommitmentAmount > MAXIMUM_COMMIT_ETH)
            _canCommitmentAmount = MAXIMUM_COMMIT_ETH;
        uint256 _refundAmount = _commitment.sub(_canCommitmentAmount);
        _commitment = _canCommitmentAmount;
        _safeTransferETH(_addr, _refundAmount);
    } else if (_commitment.add(marketStatus.commitmentsTotal) > marketInfo.commitmentCap) {
        uint256 _canCommitmentAmount = marketInfo.commitmentCap.sub(marketStatus.commitmentsTotal);
        uint256 _refundAmount = _commitment.sub(_canCommitmentAmount);
        _commitment = _canCommitmentAmount;
        _safeTransferETH(_addr, _refundAmount);
    }
    uint256 newCommitment = commitments[_addr].add(_commitment);
    require(newCommitment >= MINIMUM_COMMIT_ETH, "SbSale: less than minimum commitment amount");
    commitments[_addr] = newCommitment;
    marketStatus.commitmentsTotal = marketStatus.commitmentsTotal.add(_commitment);
    emit AddedCommitment(_addr, _commitment, _referral);
}
```

## Recommendation
Revise the above routine to ensure the MAXIMUM_COMMIT_ETH parameter is properly honored. Similarly, the same issue occurs to the _addWhaleCommitment() routine regarding the WHALE_MAXIMUM_COMMIT_ETH enforcement.
