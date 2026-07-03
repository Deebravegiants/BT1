### Title
`account != msg.sender` Guard in `KernelMerkleDistributor::_processClaim` Permanently Freezes KERNEL Rewards for Smart Contract Recipients - (File: contracts/KERNEL/KernelMerkleDistributor.sol)

---

### Summary

`KernelMerkleDistributor::_processClaim` enforces `if (account != msg.sender) revert Unauthorized()`, which means only the exact `account` address can trigger its own claim. Any smart contract address included in the merkle distribution that lacks an internal function to call `claim` or `claimAndStake` will have its KERNEL rewards permanently frozen.

---

### Finding Description

`KernelMerkleDistributor` distributes KERNEL tokens to addresses listed in a merkle tree. Both `claim` and `claimAndStake` delegate to the internal `_processClaim`, which enforces:

```solidity
// contracts/KERNEL/KernelMerkleDistributor.sol L311-313
if (account != msg.sender) {
    revert Unauthorized();
}
```

The public `claim` signature accepts an `account` parameter described as "The address to send the token to," implying third-party claiming is a supported design intent. However, the guard unconditionally blocks any caller that is not `account` itself.

Smart contracts — vaults, pools, multisigs, or any protocol-level address — that are included as recipients in the merkle tree but do not implement a dedicated function to call `claim` or `claimAndStake` on `KernelMerkleDistributor` cannot claim their allocated KERNEL. No admin escape hatch exists in the contract to recover or redirect these tokens.

---

### Impact Explanation

**Medium — Permanent freezing of unclaimed yield.**

KERNEL tokens allocated to a smart contract recipient in the merkle tree are irrecoverably locked if that contract cannot itself call `claim`. The tokens remain in `KernelMerkleDistributor` with no recovery path, because:
- No owner/admin function exists to sweep unclaimed tokens to an alternate address.
- The `account != msg.sender` check cannot be bypassed by any unprivileged caller.
- The merkle state for that `account` is never updated, so the allocation is permanently stranded.

---

### Likelihood Explanation

**Medium.** The KERNEL ecosystem explicitly supports staking on behalf of other addresses (`KernelDepositPool::stakeFor` with `STAKE_FOR_ROLE`), and `claimAndStake` is designed to stake directly into `KernelDepositPool` for `account`. It is realistic that protocol-controlled contracts (e.g., liquidity pools, vaults, or reward routers) are included as merkle recipients. Any such contract without a bespoke claim function triggers this freeze with no user error required.

---

### Recommendation

Remove the `account != msg.sender` guard from `_processClaim`. The merkle proof already cryptographically binds `index`, `account`, and `cumulativeAmount`, so only a caller holding a valid proof for `account` can succeed. No additional caller-identity check is needed for security. This mirrors the fix applied in the referenced external report (removing the analogous `!isHolder` guard).

Alternatively, introduce a delegated-claimer mapping (similar to EigenLayer's `claimerFor`) so accounts can pre-authorize a third-party address to claim on their behalf.

---

### Proof of Concept

1. Protocol off-chain script builds a merkle tree that includes `address(vaultContract)` with a non-zero `cumulativeAmount`.
2. `KernelMerkleDistributor::setMerkleRoot` is called with the new root.
3. Any EOA calls:
   ```solidity
   kernelMerkleDistributor.claim(index, address(vaultContract), amount, proof);
   ```
4. `_processClaim` executes `if (account != msg.sender)` → `address(vaultContract) != msg.sender` → `revert Unauthorized()`.
5. `vaultContract` itself has no function to call `claim`, so it also cannot self-claim.
6. The KERNEL allocation for `vaultContract` is permanently frozen in `KernelMerkleDistributor`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L250-266)
```text
    function claim(
        uint256 index,
        address account,
        uint256 cumulativeAmount,
        bytes32[] calldata merkleProof
    )
        external
        override
        nonReentrant
        whenNotPaused
    {
        uint256 amountToSend = _processClaim(index, account, cumulativeAmount, merkleProof);

        kernel.safeTransfer(account, amountToSend);

        emit Claimed(index, account, amountToSend);
    }
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L270-285)
```text
    function claimAndStake(
        uint256 index,
        address account,
        uint256 cumulativeAmount,
        bytes32[] calldata merkleProof
    )
        external
        nonReentrant
        whenNotPaused
    {
        uint256 amountToStake = _processClaim(index, account, cumulativeAmount, merkleProof);

        IKernelDepositPool(kernelDepositPool).stakeFor(account, amountToStake);

        emit ClaimedAndStaked(index, account, amountToStake);
    }
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L292-313)
```text
    function _processClaim(
        uint256 index,
        address account,
        uint256 cumulativeAmount,
        bytes32[] calldata merkleProof
    )
        internal
        returns (uint256)
    {
        UtilLib.checkNonZeroAddress(account);

        if (currentMerkleRoot == bytes32(0)) {
            revert ZeroValueProvided();
        }

        if (index == 0 || index > currentIndex) {
            revert InvalidIndex();
        }

        if (account != msg.sender) {
            revert Unauthorized();
        }
```
