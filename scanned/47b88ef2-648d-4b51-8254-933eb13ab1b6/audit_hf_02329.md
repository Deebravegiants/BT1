# [M] Incorrect Index Value Used in remove()

## Summary
Severity: Medium
Contest weight: 0.4506
Dataset id: 12653
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The FarmBooster contract maintains a state variable (i.e. mapping(address => ItMap) public userInfo) which records the pid-multiplier pairs for each users proxy. The pid-multiplier pair is represented with the ItMap struct which is implemented in the IterableMapping library. While examining the logic to add and remove a pid-multiplier entry, we notice the existence of using an incorrect key index. To elaborate, we show below code snippet from the IterableMapping library. As the names indicate, the insert() routine is used to insert a key/value pair, and the remove() routine is used to remove the pair of the input key. In the insert() routine, the key is pushed into an array keys and the index of key in keys is recorded by the indexs[key]. Note that the index value starts from 1, not 0. In the remove() routine, it gets the index of the input key and moves the last key from the end of the keys to the index of the key to be removed. And then, it updates the indexs[lastKey] to index - 1 (line 37) which is incorrect. By design, the indexs[lastKey] shall be updated to index which is the index of the removed key.

```solidity
function insert(
    ItMap storage self,
    uint256 key,
    uint256 value
) internal {
    uint256 keyIndex = self.indexs[key];
    self.data[key] = value;
    if (keyIndex > 0) return;
    else {
        self.indexs[key] = self.keys.length + 1;
        self.keys.push(key);
        return;
    }
}

function remove(ItMap storage self, uint256 key) internal {
    uint256 index = self.indexs[key];
    if (index == 0) return;
    uint256 lastKey = self.keys[self.keys.length - 1];
    if (key != lastKey) {
        self.keys[index - 1] = lastKey;
        self.indexs[lastKey] = index - 1;
    }
    delete self.data[key];
    delete self.indexs[key];
    self.keys.pop();
}
```

## Recommendation
Revise the above mentioned remove() routine to correctly update the indexs[key].
