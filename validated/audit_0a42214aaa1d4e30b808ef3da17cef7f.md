### Title
`renounceOwnership()` Not Overridden in `KernelMerkleDistributor` Permanently Freezes Undistributed KERNEL Tokens and Blocks Future Reward Rounds - (File: contracts/KERNEL/KernelMerkleDistributor.sol)

---

### Summary

`KernelMerkleDistributor` inherits `OwnableUpgradeable` without overriding `renounceOwnership()`. If the owner calls this inherited function, all `onlyOwner`-gated operations — including `setMerkleRoot()`, `pause()`/`unpause()`, `setKernelDepositPool()`, and `setProtocolTreasury()` — become permanently inaccessible. Because the contract has no token-recovery function, any KERNEL tokens held for future distribution rounds are permanently frozen.

---

### Finding Description

`KernelMerkleDistributor` is an upgradeable contract that distributes KERNEL tokens to users across multiple sequential distribution rounds. Each round requires the owner to call `setMerkleRoot()` to advance `currentIndex` and set the new root before users can claim. [1](#0-0) 

The contract inherits `OwnableUpgradeable`: [2](#0-1) 

OpenZeppelin's `OwnableUpgradeable` exposes a public `renounceOwnership()` function that sets `_owner` to `address(0)`. Neither `KernelMerkleDistributor` nor any of its parents override this function to revert. [3](#0-2) 

After `renounceOwnership()` is called, every `onlyOwner` function permanently reverts:

- `setMerkleRoot()` — no new distribution rounds can ever be opened
- `pause()` / `unpause()` — emergency circuit-breaker is permanently disabled
- `setKernelDepositPool()` — the staking integration cannot be updated
- `setProtocolTreasury()` / `setFeeInBPS()` — fee routing is frozen [4](#0-3) 

Critically, the contract contains **no token-recovery or `withdrawTokens()` function**. Any KERNEL tokens pre-funded for future distribution rounds remain locked in the contract with no on-chain path to retrieve them.

The same structural gap exists in `MerkleDistributor` and `MerkleBlastPointsDistributor`, which also inherit `OwnableUpgradeable` without overriding `renounceOwnership()`. [5](#0-4) 

---

### Impact Explanation

**Critical — Permanent freezing of funds.**

KERNEL tokens deposited into `KernelMerkleDistributor` for future distribution rounds cannot be recovered once ownership is renounced. There is no `withdrawTokens()`, no `rescueTokens()`, and no upgrade path that bypasses the `onlyOwner` guard (the proxy admin is a separate role and cannot call these functions). All pre-funded tokens are permanently frozen on-chain.

Additionally, `pause()` becomes permanently inaccessible, removing the emergency circuit-breaker that protects users from exploits or mispriced claims.

---

### Likelihood Explanation

**Low-Medium.** The owner must explicitly call `renounceOwnership()`. However:

1. The function is publicly visible and callable with no additional confirmation step.
2. Renouncing ownership is a recognized "decentralization" pattern that protocol teams sometimes apply to signal immutability — a plausible operational mistake given the contract's design.
3. No documentation or code comment warns that renouncing ownership permanently freezes pre-funded tokens.
4. The same pattern was flagged as a real operational risk in the referenced audit (Aera/Spearbit), confirming it is not purely theoretical.

---

### Recommendation

Override `renounceOwnership()` in `KernelMerkleDistributor`, `KernelTop100MerkleDistributor`, `MerkleDistributor`, and `MerkleBlastPointsDistributor` to unconditionally revert:

```solidity
function renounceOwnership() public override onlyOwner {
    revert("renounceOwnership disabled");
}
```

Alternatively, add a `withdrawTokens()` recovery function (as `KernelTop100MerkleDistributor` already does) so that even if ownership is renounced, a governance-controlled upgrade can recover stranded funds. [6](#0-5) 

---

### Proof of Concept

1. Protocol deploys `KernelMerkleDistributor` and pre-funds it with 1,000,000 KERNEL for the next three distribution rounds.
2. Owner calls the inherited `OwnableUpgradeable.renounceOwnership()`. `_owner` is set to `address(0)`.
3. Owner attempts to call `setMerkleRoot(newRoot)` to open round 2. Transaction reverts with `Ownable: caller is not the owner`.
4. No alternative path exists to call `setMerkleRoot()` or recover the pre-funded tokens.
5. All 1,000,000 KERNEL tokens are permanently frozen in the contract.
6. Reward claimants entitled to future rounds receive nothing; their unclaimed yield is permanently lost. [7](#0-6)

### Citations

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L9-9)
```text
import { OwnableUpgradeable } from "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L133-138)
```text
contract KernelMerkleDistributor is
    IMerkleDistributor,
    Initializable,
    OwnableUpgradeable,
    PausableUpgradeable,
    ReentrancyGuardUpgradeable
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L215-215)
```text
        __Ownable_init();
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L356-423)
```text
    function setKernelDepositPool(address _kernelDepositPool) external onlyOwner {
        UtilLib.checkNonZeroAddress(_kernelDepositPool);

        address oldKernelDepositPool = address(kernelDepositPool);
        kernelDepositPool = IKernelDepositPool(_kernelDepositPool);

        // Revoke the approval of the old KernelDepositPool contract to spend KERNEL tokens on behalf of this contract
        kernel.forceApprove(oldKernelDepositPool, 0);

        // Approve the KernelDepositPool contract to spend an unlimited amount of KERNEL tokens on behalf of this
        // contract
        kernel.forceApprove(_kernelDepositPool, type(uint256).max);

        emit KernelDepositPoolUpdated(_kernelDepositPool);
    }

    /**
     * @notice Sets the protocol treasury address
     * @param _protocolTreasury The address of the new protocol treasury
     */
    function setProtocolTreasury(address _protocolTreasury) external onlyOwner {
        UtilLib.checkNonZeroAddress(_protocolTreasury);

        protocolTreasury = _protocolTreasury;

        emit ProtocolTreasuryUpdated(protocolTreasury);
    }

    /**
     * @notice Sets the fee in basis points
     * @param _feeInBPS The new fee in basis points
     */
    function setFeeInBPS(uint256 _feeInBPS) external onlyOwner {
        if (_feeInBPS > MAX_FEE_IN_BPS) {
            revert InvalidFeeInBPS();
        }

        feeInBPS = _feeInBPS;

        emit FeeInBPSUpdated(feeInBPS);
    }

    /**
     * @notice Sets the new merkle root
     * @param _merkleRootToSet The new merkle root to be set
     */
    function setMerkleRoot(bytes32 _merkleRootToSet) external onlyOwner {
        if (_merkleRootToSet == bytes32(0)) {
            revert ZeroValueProvided();
        }

        currentMerkleRoot = _merkleRootToSet;

        currentMerkleRootIndex++;
        currentIndex++;

        emit MerkleRootSet(currentMerkleRootIndex, currentMerkleRoot);
    }

    /// @dev Pauses the contract
    function pause() external onlyOwner {
        _pause();
    }

    /// @dev Unpauses the contract
    function unpause() external onlyOwner {
        _unpause();
    }
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L44-44)
```text
contract MerkleDistributor is IMerkleDistributor, OwnableUpgradeable, PausableUpgradeable {
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
