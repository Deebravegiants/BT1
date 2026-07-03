### Title
`renounceOwnership()` Not Overridden Permanently Freezes Excess Tokens — (`contracts/KERNEL/KernelTop100MerkleDistributor.sol`)

---

### Summary

`KernelTop100MerkleDistributor` inherits from `OwnableUpgradeable` but does not override `renounceOwnership()`. The inherited function allows the owner to irrevocably set `_owner` to `address(0)`. Because `withdrawTokens` — the only mechanism to recover any KERNEL tokens held in the contract that exceed user allocations — is guarded by `onlyOwner`, renouncing ownership permanently freezes those tokens. Additionally, `pause` and `unpause` become permanently inaccessible, meaning a paused contract can never be unpaused, freezing all user claims as well.

---

### Finding Description

`KernelTop100MerkleDistributor` inherits `OwnableUpgradeable` and calls `__Ownable_init()` during initialization. [1](#0-0) [2](#0-1) 

The inherited `renounceOwnership()` from `OwnableUpgradeable` sets `_owner` to `address(0)` with no override or guard in the contract: [3](#0-2) 

The `withdrawTokens` function is the sole mechanism to recover any KERNEL (or other ERC-20) tokens held by the contract that are not allocated to users — for example, tokens sent in excess of the merkle-tree total, or tokens for users who never claim after the vesting window closes: [4](#0-3) 

`pause` and `unpause` are also exclusively `onlyOwner`: [5](#0-4) 

None of these functions have any alternative recovery path. If `renounceOwnership()` is called, all three become permanently inaccessible.

The same structural issue exists in `MerkleDistributor` and `KernelMerkleDistributor`, where `setMerkleRoot` is `onlyOwner` with no override — renouncing ownership permanently prevents any future merkle root updates, freezing all future yield distributions: [6](#0-5) [7](#0-6) 

---

### Impact Explanation

**Primary (Critical — Permanent freezing of funds):** Any KERNEL tokens held in `KernelTop100MerkleDistributor` beyond what users can claim via the merkle tree are permanently frozen if `renounceOwnership()` is called, because `withdrawTokens` is the only recovery path and it requires `onlyOwner`.

**Secondary (Critical — Permanent freezing of funds):** If the contract is paused at the time ownership is renounced, `unpause` is also permanently inaccessible, freezing all user claims — including tokens that are legitimately allocated to users.

**Tertiary (Medium — Permanent freezing of unclaimed yield):** In `MerkleDistributor` and `KernelMerkleDistributor`, renouncing ownership prevents any future `setMerkleRoot` calls, permanently halting all future reward distributions.

---

### Likelihood Explanation

The owner is a privileged role, but `renounceOwnership()` is a standard, publicly visible function inherited from OpenZeppelin with no friction or confirmation step. It can be called accidentally (e.g., mistaking it for a different admin action) or as part of a misguided "decentralization" step. No attacker action is required — the owner alone triggers the irreversible state. The likelihood is low-to-medium but the consequence is irreversible.

---

### Recommendation

Override `renounceOwnership()` in all affected contracts to always revert, preventing accidental or intentional ownership renouncement:

```solidity
function renounceOwnership() public override onlyOwner {
    revert("Ownership cannot be renounced");
}
```

Affected files:
- `contracts/KERNEL/KernelTop100MerkleDistributor.sol`
- `contracts/KERNEL/KernelMerkleDistributor.sol`
- `contracts/utils/MerkleDistributor/MerkleDistributor.sol`
- `contracts/utils/MerkleDistributor/MerkleBlastPointsDistributor.sol`

---

### Proof of Concept

1. Owner deploys `KernelTop100MerkleDistributor` and funds it with 1,000,000 KERNEL tokens (e.g., 900,000 allocated to users via merkle tree, 100,000 as buffer/excess).
2. Owner calls `renounceOwnership()` — inherited from `OwnableUpgradeable`, sets `_owner = address(0)`.
3. Owner attempts to call `withdrawTokens(kernelAddress, 100_000e18, treasury)` to recover the excess — reverts with `"Ownable: caller is not the owner"` because `_owner` is now `address(0)`.
4. The 100,000 excess KERNEL tokens are permanently locked in the contract with no recovery path.
5. If the contract was paused before step 2, `unpause()` also reverts permanently, freezing the remaining 900,000 KERNEL tokens allocated to users as well. [4](#0-3) [3](#0-2)

### Citations

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L111-117)
```text
contract KernelTop100MerkleDistributor is
    IMerkleDistributor,
    Initializable,
    OwnableUpgradeable,
    PausableUpgradeable,
    ReentrancyGuardUpgradeable
{
```

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L208-208)
```text
        __Ownable_init();
```

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L461-472)
```text
    function withdrawTokens(address _token, uint256 _amount, address _recipient) external onlyOwner {
        UtilLib.checkNonZeroAddress(_token);
        UtilLib.checkNonZeroAddress(_recipient);

        if (_amount == 0) {
            revert ZeroValueProvided();
        }

        IERC20(_token).safeTransfer(_recipient, _amount);

        emit TokensWithdrawn(_token, _amount, _recipient);
    }
```

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L475-482)
```text
    function pause() external onlyOwner {
        _pause();
    }

    /// @notice Unpauses the contract
    function unpause() external onlyOwner {
        _unpause();
    }
```

**File:** lib/openzeppelin-contracts-upgradeable/contracts/access/OwnableUpgradeable.sol (L66-68)
```text
    function renounceOwnership() public virtual onlyOwner {
        _transferOwnership(address(0));
    }
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L156-167)
```text
    function setMerkleRoot(bytes32 _merkleRootToSet) external onlyOwner {
        if (_merkleRootToSet == bytes32(0)) {
            revert ZeroValueProvided();
        }

        currentMerkleRoot = _merkleRootToSet;

        currentMerkleRootIndex++;
        currentIndex++;

        emit MerkleRootSet(currentMerkleRootIndex, currentMerkleRoot);
    }
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L402-413)
```text
    function setMerkleRoot(bytes32 _merkleRootToSet) external onlyOwner {
        if (_merkleRootToSet == bytes32(0)) {
            revert ZeroValueProvided();
        }

        currentMerkleRoot = _merkleRootToSet;

        currentMerkleRootIndex++;
        currentIndex++;

        emit MerkleRootSet(currentMerkleRootIndex, currentMerkleRoot);
    }
```
