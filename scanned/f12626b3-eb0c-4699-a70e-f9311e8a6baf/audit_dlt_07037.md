# [M] M-03 Unmitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-ai-arena-mitigation
Published: 2024-04-10
Source: https://github.com/code-423n4/2024-04-ai-arena-mitigation-findings/issues/8
Type: code-finding

## Details
# Lines of code

https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/d81beee0df9c5465fe3ae954ce41300a9dd60b7f/src/MergingPool.sol#L158-L169


# Vulnerability details

### C4 issue
M-03: [Fighter created by mintFromMergingPool can have arbitrary weight and element](https://github.com/code-423n4/2024-02-ai-arena-findings/issues/932)

### Comments
When users minted new fighters through the MergingPool, validation for `weight` and `element` values, passed as input in the `customAttributes` array, was missing. Therefore, winners of MergingPool NFTs could arbitrarily assign any `weight` and `element` to their new fighters. 

### Mitigation
[PR #16](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/pull/16)
The fixed implemented introduces input validation for the custom attributes provided in `MergingPool::claimRewards`. `element` is required to be smaller than the total number of possible elements for the current generation, while `weight` is required to be in the [65, 95] range:

```solidity
require(customAttributes[j][0] < _fighterFarmInstance.numElements(generation), "MergingPool: element out of bounds");
require(customAttributes[j][1] >= 65 && customAttributes[j][1] <= 95, "MergingPool: weight out of bounds");
```

Users calling claimRewards provide one pair of customAttribute per claimable NFT. However, the `customAttributes` index [checked](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/d81beee0df9c5465fe3ae954ce41300a9dd60b7f/src/MergingPool.sol#L159-L160) is not the appropriate index `claimIndex` but the `winnerAddresses` index `j`. 

The most concerning consequence of this bug is that the custom attribute values could bypass the element and weight requirements if the custom attribute index for a given claim is greater than the max number of winners of the rounds iterated. For example, if there is 1 winner per round for several rounds in a row and a player wins two rounds, `customAttributes[1]` would not be checked and `customAttributes[0]` would be checked repeatedly.

### Suggestion
Change
```solidity
for (uint32 j = 0; j < winnersLength; j++) {
    require(customAttributes[j][0] < _fighterFarmInstance.numElements(generation), "MergingPool: element out of bounds");
    require(customAttributes[j][1] >= 65 && customAttributes[j][1] <= 95, "MergingPool: weight out of bounds");
    if (msg.sender == winnerAddresses[currentRound][j]) {
        _fighterFarmInstance.mintFromMergingPool(
            msg.sender,
            modelURIs[claimIndex],
            modelTypes[claimIndex],
            customAttributes[claimIndex]
        );
        claimIndex += 1;
    }
}
```
to:
```solidity
for (uint32 j = 0; j < winnersLength; j++) {
    if (msg.sender == winnerAddresses[currentRound][j]) {
        require(customAttributes[claimIndex][0] < _fighterFarmInstance.numElements(generation), "MergingPool: element out of bounds");
        require(customAttributes[claimIndex][1] >= 65 && customAttributes[claimIndex][1] <= 95, "MergingPool: weight out of bounds");
        _fighterFarmInstance.mintFromMergingPool(
            msg.sender,
            modelURIs[claimIndex],
            modelTypes[claimIndex],
            customAttributes[claimIndex]
        );
        claimIndex += 1;
    }
}
```

### Conclusion
The implemented mitigation is incorrect. In some scenarios, the element and weight values input in `MergingPool::claimRewards` could still be arbitrarily set, ignoring the intended input validation. 





## Assessed type

Invalid Validation
