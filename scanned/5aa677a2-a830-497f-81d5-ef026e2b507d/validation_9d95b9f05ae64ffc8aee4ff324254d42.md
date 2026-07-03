### Title
Single-Step Ownership Transfer in `KernelTop100MerkleDistributor` Permanently Freezes Undistributed KERNEL Tokens - (File: contracts/KERNEL/KernelTop100MerkleDistributor.sol)

### Summary
`KernelTop100MerkleDistributor` inherits `OwnableUpgradeable`, which implements a single-step ownership transfer. If the admin mistypes the new owner address, ownership is irrecoverably lost. All `onlyOwner`-gated functions — including `withdrawTokens`, `pause`, `setKernelDepositPool`, `setProtocolTreasury`, and `setFeeInBPS` — become permanently uncallable, freezing any undistributed KERNEL tokens held in the contract.

### Finding Description
`KernelTop100MerkleDistributor` inherits `OwnableUpgradeable` from OpenZeppelin's upgradeable library. [1](#0-0) 

`OwnableUpgradeable.transferOwnership` immediately overwrites `_owner` with the supplied address in a single atomic step, with no pending-owner confirmation mechanism. [2](#0-1) [3](#0-2) 

If the admin passes a wrong address (e.g., a typo, a zero address that bypasses the non-zero check, or a miscopied address), ownership is permanently transferred to an uncontrolled account. Every `onlyOwner` function in the contract then reverts unconditionally.

The critical `onlyOwner` functions that become permanently inaccessible are:

- `withdrawTokens` — the **only** mechanism to recover KERNEL tokens remaining in the contract after the 30-day vesting window closes. [4](#0-3) 

- `pause` / `unpause` — emergency circuit-breaker for `claim` and `claimAndStake`. [5](#0-4) 

- `setKernelDepositPool` — required to update the staking target for `claimAndStake`. [6](#0-5) 

The same single-step pattern is present in three additional production contracts:
- `contracts/KERNEL/KernelMerkleDistributor.sol` (line 9, `OwnableUpgradeable`) — `setMerkleRoot` becomes uncallable, blocking all future KERNEL distributions. [7](#0-6) 
- `contracts/utils/MerkleDistributor/MerkleDistributor.sol` (line 4, `OwnableUpgradeable`) — `setMerkleRoot` and `setToken` become uncallable. [8](#0-7) 
- `contracts/cross-chain/CrossChainRateProvider.sol` (line 4, non-upgradeable `Ownable`) — `updateRateReceiver` and `updateDstChainId` become uncallable, breaking cross-chain rate propagation. [9](#0-8) 

Note: `contracts/ccip/ConfirmedOwnerWithProposal.sol` already implements a correct two-step pattern (`transferOwnership` + `acceptOwnership`) and is not affected. [10](#0-9) 

### Impact Explanation
**Medium — Permanent freezing of unclaimed yield.**

`KernelTop100MerkleDistributor` holds KERNEL tokens for a fixed 30-day vesting window. After vesting ends, any tokens not claimed by users can only be recovered via `withdrawTokens`. If ownership is lost, those tokens are permanently locked in the contract with no recovery path. Additionally, the inability to call `pause` means the contract cannot be halted in an emergency, and the inability to call `setKernelDepositPool` means the `claimAndStake` path can become broken if the downstream pool is ever migrated.

### Likelihood Explanation
**Low.** Requires the current owner to call `transferOwnership` with an incorrect address — a realistic but infrequent operational mistake (e.g., clipboard error, address from a different network, or a recently-deprecated address).

### Recommendation
Replace `OwnableUpgradeable` with `Ownable2StepUpgradeable` (already present in the repository at `lib/openzeppelin-contracts-upgradeable/contracts/access/Ownable2StepUpgradeable.sol`) in all four affected contracts. The two-step pattern requires the nominated address to call `acceptOwnership`, ensuring ownership is never transferred to an address that cannot sign transactions.

For the non-upgradeable `CrossChainRateProvider`, `CrossChainRateReceiver`, and `MultiChainRateProvider`, replace `Ownable` with `Ownable2Step` (present at `lib/openzeppelin-contracts/contracts/access/Ownable2Step.sol`).

### Proof of Concept
1. Deploy `KernelTop100MerkleDistributor` and fund it with KERNEL tokens.
2. Vesting period begins; users partially claim over 30 days; some tokens remain unclaimed.
3. Admin calls `transferOwnership(wrongAddress)` — ownership is immediately transferred.
4. Admin attempts `withdrawTokens(kernel, remainingBalance, treasury)` — reverts with `"Ownable: caller is not the owner"`.
5. No recovery path exists; remaining KERNEL tokens are permanently locked in the contract.

### Citations

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L9-9)
```text
import { OwnableUpgradeable } from "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
```

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L398-410)
```text
    function setKernelDepositPool(address _kernelDepositPool) external onlyOwner {
        UtilLib.checkNonZeroAddress(_kernelDepositPool);

        address oldKernelDepositPool = address(kernelDepositPool);

        // Revoke old approval and set new one
        kernel.forceApprove(oldKernelDepositPool, 0);
        kernel.forceApprove(_kernelDepositPool, type(uint256).max);

        kernelDepositPool = IKernelDepositPool(_kernelDepositPool);

        emit KernelDepositPoolUpdated(_kernelDepositPool);
    }
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

**File:** lib/openzeppelin-contracts-upgradeable/contracts/access/OwnableUpgradeable.sol (L74-77)
```text
    function transferOwnership(address newOwner) public virtual onlyOwner {
        require(newOwner != address(0), "Ownable: new owner is the zero address");
        _transferOwnership(newOwner);
    }
```

**File:** lib/openzeppelin-contracts-upgradeable/contracts/access/OwnableUpgradeable.sol (L83-87)
```text
    function _transferOwnership(address newOwner) internal virtual {
        address oldOwner = _owner;
        _owner = newOwner;
        emit OwnershipTransferred(oldOwner, newOwner);
    }
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L9-9)
```text
import { OwnableUpgradeable } from "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L4-4)
```text
import { OwnableUpgradeable } from "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
```

**File:** contracts/cross-chain/CrossChainRateProvider.sol (L4-4)
```text
import { Ownable } from "@openzeppelin/contracts/access/Ownable.sol";
```

**File:** contracts/ccip/ConfirmedOwnerWithProposal.sol (L36-51)
```text
    function transferOwnership(address to) public override onlyOwner {
        _transferOwnership(to);
    }

    /**
     * @notice Allows an ownership transfer to be completed by the recipient.
     */
    function acceptOwnership() external override {
        require(msg.sender == s_pendingOwner, "Must be proposed owner");

        address oldOwner = s_owner;
        s_owner = msg.sender;
        s_pendingOwner = address(0);

        emit OwnershipTransferred(oldOwner, msg.sender);
    }
```
