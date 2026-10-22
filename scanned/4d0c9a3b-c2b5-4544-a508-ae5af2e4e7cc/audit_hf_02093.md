# [C] Revisited Logic of MaGaugeV2Upgradeable::split()

## Summary
Severity: Critical
Contest weight: 0.6371
Dataset id: 11817
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The MaGaugeV2Upgradeable contract implements an incentive mechanism, which allows the user to deposit the supported LP token to earn the CHR token. Meanwhile, an maNFT is minted to uniquely identify the user's deposit position. In particular, one entry routine, i.e., split(), is designed to split the given deposit position (specified by the input _maNFTId) into multiple new smaller positions according to the user specified weights. While examining its logic, we observe its current implementation needs to be improved.

To elaborate, we show below the related code snippet of the contract. Inside the split() routine, the given maNFT (representing the previous deposit position) is burnt (line 527) and multiple new maNFTs are minted (line 510) to represent the new deposit positions. However, we observe the reward-related state variables (e.g., idRewardPerTokenPaid and _positionLastWeights) are not timely initialized when the new maNFT is minted, which will result in the user getting more rewards than expected.

Moreover, we observe the reward of the previous deposit position is not timely transferred to the user. Apparently, it ignores the fact that the user will not be able to claim the reward after the corresponding maNFT is burnt. Note another routine, i.e., merge(), shares the same issue.
```solidity
function split(
    uint _maNFTId,
    uint[] calldata weights
) external nonReentrant isNotEmergency updateTotalWeight updateReward(_maNFTId) {
    require(
        _isApprovedOrOwner(_msgSender(), _maNFTId),
        "maNFT: caller is not token owner or approved"
    );
    // limit the weights length to avoid out of gas
    require(weights.length <= MAX_SPLIT_WEIGHTS, "Max splitted positions exceeded");
    uint weightsSum = 0;
    for (uint i; i < weights.length; i++) {
        weightsSum += weights[i];
        uint splitAmount = (weights[i] * _lpBalances[_maNFTId]) / WEIGHTS_MAX_POINTS;
        require(splitAmount > 0, "deposit(Gauge): cannot stake 0");
        uint _newMANFTId = tokenId;
        _mint(_msgSender(), _newMANFTId); // potentially , use ownerOf(_maNFTId)
        tokenId++;
        _lpBalances[_newMANFTId] = splitAmount;
        _positionEntries[_newMANFTId] = _positionEntries[_maNFTId];
        _nftToEpochIds[_newMANFTId] = _nftToEpochIds[_maNFTId];
    }
    // bps accuracy is used for e.g.
    require(weightsSum == WEIGHTS_MAX_POINTS, "Invalid weights sum");
    // total weight doesn't change as liquidity and maturity didn't change
    _lpBalances[_maNFTId] = 0;
    _positionEntries[_maNFTId] = 0;
    _positionLastWeights[_maNFTId] = 0;
    _nftToEpochIds[_maNFTId] = 0;
    _burn(_maNFTId);
    emit Split(_msgSender(), _maNFTId); // potentially , use owner of nft
}
```

## Recommendation
Timely distribute the reward before the maNFT is burnt and initialize the reward-related state variables when the new maNFT is minted.
