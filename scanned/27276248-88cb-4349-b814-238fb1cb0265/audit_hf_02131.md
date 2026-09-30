# [M] Incorrect Epoch Removal Logic In VaultFarm::removePoolEpoch

## Summary
Severity: Medium
Contest weight: 0.4292
Dataset id: 11962
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The VaultFarm contract provides an external removePoolEpoch() function for the privileged Owner account to remove a specified epoch token from a specified pool. Our analysis with this routine shows its current logic is not correct.
To elaborate, we show below its code snippet. It comes to our attention that there is a lack of pending rewards handling and related storage arrays epochs/epochRewards updates before removing an epoch token from a pool. If the storage arrays epochs/epochRewards are not updated timely, this removed epoch token will be added to the pool again if the newPool()/updatePool()/appendReward() functions are called by the privileged Owner account.
```solidity
function removePoolEpoch(address pool , address epoch) external onlyOwner {
    Pool(pool).remove(epoch);
}
// remove some item for saving gas (array issue).
// should only used when no such epoch assets.
function remove(address epoch) external onlyFarming {
    require(validEpoches[epoch], "Not a valid epoch");
    validEpoches[epoch] = false;
    uint len = epoches.length;
    for (uint i = 0; i < len; i++) {
        if (epoch == epoches[i]) {
            if (i == len - 1) {
                epoches.pop();
                break;
            } else {
                epoches[i] = epoches[len - 1];
                epoches.pop();
                break;
            }
        }
    }
}
```

## Recommendation
Add pending rewards handling and storage arrays epoches/epochRewards updates logic before removing an epoch token from a pool.
