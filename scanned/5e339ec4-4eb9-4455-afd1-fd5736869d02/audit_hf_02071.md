# [M] Possible DoS With _getRandomMultiplier() Pre-Validation

## Summary
Severity: Medium
Contest weight: 0.4599
Dataset id: 11737
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Binopoly has an essential BrickFactory contract to allow for tokenized materials and their assembly. During the examination of the logic to claim upgraded materials, we observe the randomness factor that is designed to compute the success ratio (via _getRandomSuccessRate()). However, this randomness computation may not be truly randomized and the caller may take advantage of it to choose to not claim the upgraded materials if the success ratio is not desired. In the following, we use the related claimUpgratedMaterial() function. It has a rather straightforward logic and makes use of the helper routine _getRandomSuccessRate() to compute the upgratedAmount (line 326 and 334). However, the helper routine can be readily pre-computed to decide whether the success ratio is desired. If not, the caller may choose not to claim.

```solidity
function claimUpgratedMaterial(uint256 lineId) public {
    require(lineId != 0, "can not process line #0");
    FactoryAttributes storage thisLevelAttributes = _currentAttributes[currentLevel];
    require(thisLevelAttributes.productionLineLimit >= lineId, "exceed production line limit");
    require(isReadyToClaim(lineId), "not ready to claim now, try later");
    address lineOwner = _linesUsage.get(lineId);
    uint256 finishTime = _completeTime[lineId];
    uint256 processAmount = _processAmounts[lineId];
    uint256 upgratedAmount;
    if (_msgSender() == lineOwner) {
        uint256 baseRate = thisLevelAttributes.baseSuccessRate;
        uint256 claimRate = _getRandomSuccessRate(baseRate);
        require(claimRate <= 10000, "claimRate exceed 100%");
        upgratedAmount = processAmount.mul(claimRate).div(10000);
        materialsAddress.mint(lineOwner, advanceMaterialId, upgratedAmount, "");
    } else {
        require(block.timestamp > finishTime.add(PROTECTION_PERIOD), "can not claim within protection time");
        uint256 baseRate = thisLevelAttributes.baseSuccessRate;
        uint256 claimRate = _getRandomSuccessRate(baseRate);
        require(claimRate <= 10000, "claimRate exceed 100%");
        upgratedAmount = processAmount.mul(claimRate).div(10000);
        uint256 shareAmount = upgratedAmount.div(10); // 10%
        uint256 ownerAmount = upgratedAmount.sub(shareAmount); // 90%
        materialsAddress.mint(lineOwner, advanceMaterialId, ownerAmount, "");
        materialsAddress.mint(_msgSender(), advanceMaterialId, shareAmount, "");
    }
    // remove and set to 0
    _linesUsage.remove(lineId);
    _completeTime[lineId] = 0;
    _processAmounts[lineId] = 0;
    emit ClaimUpgratedMaterial(lineId, lineOwner, upgratedAmount);
}

// generate a random integer between 0.9* base to 1.1* base (upperBound can not exceed 10000)
function _getRandomSuccessRate(uint256 base) private view returns (uint256) {
    // +/- 10%
    uint256 halfRange = base.div(10);
    uint256 lowerBound = base.sub(halfRange);
    uint256 upperBound = base.add(halfRange) >= 10000 ? 10000 : base.add(halfRange);
    uint256 randomInt = uint256(
        keccak256(
            abi.encodePacked(
                uint256(blockhash(block.number.sub(1))),
                uint256(block.coinbase),
                block.difficulty,
                block.timestamp,
                base
            )
        )
    ).mod(upperBound.sub(lowerBound).add(1));
    return randomInt.add(lowerBound);
```

In addition, the HousesNFT contract has a similar _getRandomMultiplier() routine that can be similarly computed to block possible safeMint() operations.

## Recommendation
Improve the randomness design in the above two functions and prevent them from being exploited.
