# [M] Revisited Logic in merge()

## Summary
Severity: Medium
Contest weight: 0.4614
Dataset id: 13239
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Tetu v2 protocol, the VeTetu contract implements a Vote-Escrow NFT, which gives users the ability to vote on proposals. Specially, it provides the function for a user to merge his/her NFTs. While reviewing the logic to merge the NFTs, we notice the current end time of the target NFT may not be given correctly.
To elaborate, we show below the code snippet of the merge() routine. As the name indicates, it is used to merge two NFTs of the same user. By design, the new end time of the target NFT shall be the bigger one from the end times of both NFTs. However, in the first call to the _depositFor() routine, we notice the lockedEnd parameter which represents the current end time of the target NFT is set to end directly (line 1024). If the end time of the from NFT is bigger, the end is set to the end time of the from NFT, which is not the current end time of the target NFT. If the lockedEnd parameter is not given correctly, some state variables may become unexpected in the _checkpoint() routine, including the latest check point in the _pointHistory[] and the slope change of the old end time in the slopeChanges[].
```solidity
function merge(uint _from, uint _to) external nonReentrant {
    require(attachments[_from] == 0 && voted[_from] == 0, ATTACHED);
    require(_from != _to, IDENTICAL_ADDRESS);
    require(_idToOwner[_from] == msg.sender && _idToOwner[_to] == msg.sender, NOT_OWNER);
    uint lockedEndFrom = lockedEnd[_from];
    uint lockedEndTo = lockedEnd[_to];
    public uint end = lockedEndFrom >= lockedEndTo ? lockedEndFrom : lockedEndTo;
    uint oldDerivedAmount = lockedDerivedAmount[_from];
    uint length = tokens.length;
    for (uint i; i < length; i++) {
        address stakingToken = tokens[i];
        uint _lockedAmountFrom = lockedAmounts[_from][stakingToken];
        if (_lockedAmountFrom == 0) {
            continue;
        }
        lockedAmounts[_from][stakingToken] = 0;
        _depositFor(DepositInfo({
            stakingToken: stakingToken,
            tokenId: _to,
            value: _lockedAmountFrom,
            unlockTime: end,
            lockedAmount: lockedAmounts[_to][stakingToken],
            lockedDerivedAmount: lockedDerivedAmount[_to],
            lockedEnd: end,
            depositType: DepositType.MERGE_TYPE
        }));
        emit Merged(stakingToken, msg.sender, _from, _to);
```

## Recommendation
Revisit the logic in the above merge() routine and set the lockedEnd parameter to the current end time of the target NFT in the first call to the _depositFor() routine.
