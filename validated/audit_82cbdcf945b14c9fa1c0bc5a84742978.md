### Title
Hardcoded `account != msg.sender` guard in `_processClaim` permanently freezes unclaimed KERNEL yield for any contract-address recipient that cannot self-initiate an external call — (`contracts/KERNEL/KernelMerkleDistributor.sol`)

---

### Summary

`_processClaim` unconditionally requires `account == msg.sender`. Any address in the merkle tree that is a smart contract without a built-in mechanism to call `claim` or `claimAndStake` on this distributor (e.g. a simple vault, a pure-receive contract, or any contract whose execution logic does not include an outbound call to this distributor) can never collect its allocated KERNEL yield. No third-party relayer, keeper, or EOA can substitute, because the guard reverts every such attempt with `Unauthorized`.

---

### Finding Description

In `_processClaim` (line 311–313):

```solidity
if (account != msg.sender) {
    revert Unauthorized();
}
``` [1](#0-0) 

Both public entry-points delegate to this internal function:

- `claim` (line 261) [2](#0-1) 
- `claimAndStake` (line 280) [3](#0-2) 

The guard means the **only** valid caller is the account itself. For an EOA this is always reachable. For a smart contract it is reachable only if that contract contains logic that explicitly calls `claim`/`claimAndStake` on this distributor. Contracts that lack such logic — simple vaults, pure-receive contracts, contracts whose upgrade path removed the relevant function, or any contract whose owner/admin is unavailable — can never satisfy `account == msg.sender`, so their merkle-tree allocation is permanently locked in the distributor.

There is no owner-callable rescue function, no expiry sweep, and no alternative claim path in the contract. [4](#0-3) 

---

### Impact Explanation

**Medium — Permanent freezing of unclaimed yield.**

KERNEL tokens allocated to a contract-address recipient that cannot self-call `claim` remain in the distributor indefinitely. The distributor has no admin sweep, no expiry, and no fallback path. The tokens are not lost from the contract's balance, but they are unreachable by the intended recipient and by anyone else, satisfying the definition of permanently frozen unclaimed yield.

---

### Likelihood Explanation

The merkle tree is built off-chain from on-chain activity (deposits, staking, etc.). Any contract that interacted with the protocol — a vault, a DAO treasury, a simple proxy with no `execute` function — may legitimately appear as a leaf. The protocol documentation and interface (`IMerkleDistributor`) make no restriction against contract addresses as recipients. The likelihood that at least one such address appears in a live distribution is realistic, not theoretical.

---

### Recommendation

Replace the blanket identity check with an explicit authorization model. Two standard approaches:

1. **Remove the check entirely** and rely on the merkle proof alone — the proof already cryptographically binds `(index, account, cumulativeAmount)`, so only the correct leaf can be claimed, and tokens are always sent to `account`, not to `msg.sender`.

2. **Allow approved operators per account** — let each account pre-register one or more addresses that may claim on its behalf:
   ```solidity
   mapping(address account => mapping(address operator => bool)) public approvedOperators;

   if (account != msg.sender && !approvedOperators[account][msg.sender]) {
       revert Unauthorized();
   }
   ```

Option 1 is simpler and has no security regression: the merkle proof already prevents unauthorized claims, and `kernel.safeTransfer(account, amountToSend)` already sends funds to `account`, not to the caller.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Minimal contract with NO external-call capability — simulates a simple vault
contract NoCallVault {
    // Only has a receive function; cannot call claim()
    receive() external payable {}
}

contract PoC {
    KernelMerkleDistributor distributor; // deployed & initialised
    NoCallVault vault;                   // address included in merkle tree

    function test() external {
        uint256 index = 1;
        uint256 amount = 1e18;
        bytes32[] memory proof = /* valid proof for (index, address(vault), amount) */ new bytes32[](0);

        // Attempt 1: EOA / third party calls claim on behalf of vault
        // msg.sender = address(this) != address(vault) → Unauthorized ✓
        try distributor.claim(index, address(vault), amount, proof) {
            revert("should have reverted");
        } catch (bytes memory err) {
            // reverts with Unauthorized
        }

        // Attempt 2: vault itself cannot call claim — it has no such function
        // → yield is permanently frozen, no reachable path exists
    }
}
```

The vault's allocation is provably unreachable: the only caller that satisfies `account == msg.sender` is `address(vault)` itself, but `NoCallVault` contains no function that can produce an outbound call to `claim`. [1](#0-0)

### Citations

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L261-261)
```text
        uint256 amountToSend = _processClaim(index, account, cumulativeAmount, merkleProof);
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L280-280)
```text
        uint256 amountToStake = _processClaim(index, account, cumulativeAmount, merkleProof);
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L311-313)
```text
        if (account != msg.sender) {
            revert Unauthorized();
        }
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L348-424)
```text
    /*//////////////////////////////////////////////////////////////
                            ADMIN FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /**
     * @notice Sets the KernelDepositPool contract address
     * @param _kernelDepositPool The address of the new KernelDepositPool contract
     */
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
}
```
