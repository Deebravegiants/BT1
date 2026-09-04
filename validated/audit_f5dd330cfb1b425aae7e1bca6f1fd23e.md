[1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/Merkle.sol (L26-27)
```text
        uint256 fullCount = newIndex - MINIMUM_INDEX; // number of inserted leaves
        uint256 twoPower = logarithm2(fullCount); // number of tree levels to be updated, (e.g. if 9 => 4 levels should be updated)
```

**File:** contracts/Merkle.sol (L33-34)
```text
        roots[newIndex - 1] = tree[twoPower]; // adding root to roots mapping
        return newIndex - 1;
```

**File:** contracts/Merkle.sol (L53-54)
```text
        uint256 fullCount = newIndex - MINIMUM_INDEX; // number of inserted leaves
        uint256 twoPower = logarithm2(fullCount); // number of tree levels to be updated, (e.g. if 9 => 4 levels should be updated)
```

**File:** contracts/Merkle.sol (L70-70)
```text
        roots[newIndex - 1] = tree[twoPower]; // adding root to roots mapping
```

**File:** contracts/MerkleBase.sol (L53-64)
```text
    function rootHashExists(
        uint256 _root,
        uint256 _rootIndex
    ) public view returns (bool) {
        if (m_index == MINIMUM_INDEX) {
            return _root == 0;
        }
        if (_rootIndex < MINIMUM_INDEX || _rootIndex >= m_index) {
            return false;
        }
        return _root != 0 && roots[_rootIndex] == _root;
    }
```
