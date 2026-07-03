### Title
Single-Step Ownership Transfer in `KernelTop100MerkleDistributor` Enables Permanent Freezing or Theft of Held KERNEL Tokens - (File: contracts/KERNEL/KernelTop100MerkleDistributor.sol)

---

### Summary

`KernelTop100MerkleDistributor` inherits `OwnableUpgradeable`, which implements a single-step `transferOwnership`. If the owner accidentally transfers ownership to an incorrect address, the new owner immediately and irrecoverably controls all `onlyOwner` functions — including `withdrawTokens`, which can drain the entire KERNEL token balance held in the contract. There is no confirmation step from the new owner, making any mistake permanent.

---

### Finding Description

`KernelTop100MerkleDistributor` uses `OwnableUpgradeable.__Ownable_init()` during initialization: [1](#0-0) 

The inherited `OwnableUpgradeable.transferOwnership` immediately overwrites `_owner` with the new address in a single transaction, with no pending-owner confirmation step: [2](#0-1) [3](#0-2) 

The contract holds KERNEL tokens for user distribution and exposes `withdrawTokens` as the sole admin recovery path, gated by `onlyOwner`: [4](#0-3) 

Additional `onlyOwner` functions that become permanently inaccessible on a wrong transfer include `pause`, `unpause`, `setProtocolTreasury`, `setKernelDepositPool`, and `setFeeInBPS`: [5](#0-4) 

The same single-step pattern is present in `KernelMerkleDistributor` and `MerkleDistributor`, both of which also call `__Ownable_init()` and expose `onlyOwner`-gated `setMerkleRoot` (allowing a wrong owner to redirect all future claims) and `setProtocolTreasury` (redirecting fee flows): [6](#0-5) [7](#0-6) 

`Ownable2StepUpgradeable` is already present in the repository's lib but is not used by any of these contracts: [8](#0-7) 

---

### Impact Explanation

**Critical — Direct theft of user funds / Permanent freezing of funds.**

`KernelTop100MerkleDistributor` holds the full KERNEL token supply intended for user distribution. If ownership is transferred to a wrong but non-zero address:

- **Theft path**: The wrong owner calls `withdrawTokens(kernel, balance, attacker)` and drains all KERNEL tokens before the mistake is noticed.
- **Freeze path**: If the wrong address is inaccessible (e.g., a mistyped multisig), `withdrawTokens` can never be called by the legitimate team, permanently locking all KERNEL tokens in the contract. Users cannot claim their vested tokens if the contract is paused and cannot be unpaused, or if `setKernelDepositPool` cannot be corrected.

For `KernelMerkleDistributor` and `MerkleDistributor`, a wrong owner can set a malicious `merkleRoot` to redirect all future claims to attacker-controlled addresses, constituting theft of unclaimed yield.

---

### Likelihood Explanation

Ownership transfers in these contracts will occur when handing control from the deployer to a multisig or DAO. A single typo in the target address — which is not caught by any on-chain validation beyond the zero-address check — immediately and irrecoverably transfers control. The mistake may not be noticed until an `onlyOwner` function is called and fails, by which time the wrong owner may have already acted. This is a realistic operational risk, especially across multiple contracts.

---

### Recommendation

Replace `OwnableUpgradeable` with `Ownable2StepUpgradeable` (already available in the repository) in `KernelTop100MerkleDistributor`, `KernelMerkleDistributor`, and `MerkleDistributor`. This requires the pending owner to explicitly call `acceptOwnership()`, ensuring the new address is confirmed to be accessible before control is relinquished.

```solidity
// Replace:
import { OwnableUpgradeable } from "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
// With:
import { Ownable2StepUpgradeable } from "@openzeppelin/contracts-upgradeable/access/Ownable2StepUpgradeable.sol";

// Replace inheritance:
contract KernelTop100MerkleDistributor is ..., Ownable2StepUpgradeable, ...

// Replace init call:
__Ownable2Step_init();
```

---

### Proof of Concept

1. Protocol deploys `KernelTop100MerkleDistributor` and funds it with 1,000,000 KERNEL tokens for user distribution.
2. Protocol owner calls `transferOwnership(0xWRONG_ADDRESS)` — a mistyped multisig address.
3. `OwnableUpgradeable._transferOwnership` immediately sets `_owner = 0xWRONG_ADDRESS`. No confirmation required.
4. **Theft scenario**: The controller of `0xWRONG_ADDRESS` calls `withdrawTokens(kernelAddress, 1_000_000e18, attacker)`. All KERNEL tokens are transferred to the attacker. Users receive nothing.
5. **Freeze scenario**: `0xWRONG_ADDRESS` is inaccessible. `withdrawTokens`, `pause`, `unpause`, `setProtocolTreasury`, and `setKernelDepositPool` are all permanently blocked. KERNEL tokens are frozen in the contract forever. [4](#0-3) [9](#0-8)

### Citations

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L208-208)
```text
        __Ownable_init();
```

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L461-471)
```text
    function withdrawTokens(address _token, uint256 _amount, address _recipient) external onlyOwner {
        UtilLib.checkNonZeroAddress(_token);
        UtilLib.checkNonZeroAddress(_recipient);

        if (_amount == 0) {
            revert ZeroValueProvided();
        }

        IERC20(_token).safeTransfer(_recipient, _amount);

        emit TokensWithdrawn(_token, _amount, _recipient);
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

**File:** lib/openzeppelin-contracts-upgradeable/contracts/access/OwnableUpgradeable.sol (L74-87)
```text
    function transferOwnership(address newOwner) public virtual onlyOwner {
        require(newOwner != address(0), "Ownable: new owner is the zero address");
        _transferOwnership(newOwner);
    }

    /**
     * @dev Transfers ownership of the contract to a new account (`newOwner`).
     * Internal function without access restriction.
     */
    function _transferOwnership(address newOwner) internal virtual {
        address oldOwner = _owner;
        _owner = newOwner;
        emit OwnershipTransferred(oldOwner, newOwner);
    }
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L215-215)
```text
        __Ownable_init();
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L81-81)
```text
        __Ownable_init();
```

**File:** lib/openzeppelin-contracts-upgradeable/contracts/access/Ownable2StepUpgradeable.sol (L1-1)
```text
// SPDX-License-Identifier: MIT
```
