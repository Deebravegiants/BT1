### Title
Owner can pause `KernelTop100MerkleDistributor` to freeze vested KERNEL claims, then drain all tokens via `withdrawTokens` - (File: `contracts/KERNEL/KernelTop100MerkleDistributor.sol`)

### Summary
`KernelTop100MerkleDistributor` distributes KERNEL tokens to users over a 30-day vesting schedule. Both user-facing claim functions are gated by `whenNotPaused`, and the same `onlyOwner` address that can call `pause()` can also call `withdrawTokens()` — which is **not** gated by `whenNotPaused`. A malicious owner can pause the contract to block all claims, then drain the entire KERNEL balance, permanently destroying users' vested entitlements.

### Finding Description
`claim()` and `claimAndStake()` carry the `whenNotPaused` modifier: [1](#0-0) [2](#0-1) 

`pause()` is callable exclusively by the owner: [3](#0-2) 

`withdrawTokens()` is also callable exclusively by the owner and carries **no** `whenNotPaused` guard: [4](#0-3) 

The attack sequence:
1. Owner calls `pause()` → `claim()` and `claimAndStake()` revert for all users.
2. Owner calls `withdrawTokens(address(kernel), kernel.balanceOf(address(this)), owner)` → entire KERNEL balance is transferred out while users are locked out.
3. Owner never calls `unpause()`. Users' vested allocations are permanently unclaimable and the underlying tokens are gone.

The vesting schedule accrues claimable amounts over 30 days: [5](#0-4) 

Users have a legitimate, time-accrued entitlement to these tokens. The pause + drain combination eliminates both the ability to claim and the tokens themselves.

### Impact Explanation
**Critical.** The owner can permanently freeze and directly steal all vested KERNEL tokens held in the contract. Users who have a valid merkle-proven allocation and have been accruing vested amounts over the 30-day schedule lose those funds entirely with no recovery path. This satisfies both "permanent freezing of funds" and "direct theft of any user funds."

### Likelihood Explanation
**Low.** Requires the contract owner to act maliciously or for the owner key to be compromised. No external attacker can trigger this without owner-level access. This matches the likelihood assessment of the reference report (M-04).

### Recommendation
1. Remove `whenNotPaused` from `claim()` and `claimAndStake()` so users can always retrieve their vested tokens regardless of pause state — mirroring the recommendation in the reference report.
2. Remove or strictly restrict `withdrawTokens()`. At minimum, add a check that prevents withdrawing the contract's KERNEL balance (i.e., the token being distributed), or gate it behind a timelock with a user-withdrawal grace period.

### Proof of Concept
```
// Precondition: contract holds 1,000,000 KERNEL for vested user allocations.
// Vesting has started; users have accrued claimable amounts.

// Step 1 – owner pauses
KernelTop100MerkleDistributor.pause();   // onlyOwner, no restriction

// Step 2 – user attempts to claim, reverts
KernelTop100MerkleDistributor.claim(amount, proof);
// → reverts: "Pausable: paused"

// Step 3 – owner drains while users are locked out
uint256 balance = IERC20(kernel).balanceOf(address(distributor));
KernelTop100MerkleDistributor.withdrawTokens(address(kernel), balance, owner);
// → 1,000,000 KERNEL transferred to owner; no whenNotPaused check blocks this

// Step 4 – owner never unpauses; users permanently lose vested tokens
``` [6](#0-5) [7](#0-6) [3](#0-2)

### Citations

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L261-263)
```text
        uint256 totalElapsedTime = currentTime - vestingStartTimestamp;
        uint256 totalVestedAmount = (userTotalClaimableAmount * totalElapsedTime) / VESTING_DURATION;

```

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L310-338)
```text
    function claim(uint256 amount, bytes32[] calldata merkleProof) external nonReentrant whenNotPaused {
        address user = msg.sender;

        // Verify merkle proof and update user claim data
        _verifyClaimProof(user, amount, merkleProof);

        // Get claimable amount
        uint256 claimableAmount = _getUnclaimedVestedAmount(user, amount);

        if (claimableAmount == 0) {
            revert NoTokensToClaim();
        }

        // Update user claim data
        userClaims[user].lastClaimTimestamp = block.timestamp;
        userClaims[user].amountClaimed += claimableAmount;

        // Calculate fee
        uint256 fee = (claimableAmount * feeInBPS) / FEE_DENOMINATOR;
        uint256 amountToSend = claimableAmount - fee;

        // Transfer tokens
        if (fee > 0) {
            kernel.safeTransfer(protocolTreasury, fee);
        }
        kernel.safeTransfer(user, amountToSend);

        emit Claimed(user, amountToSend);
    }
```

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L345-346)
```text
    function claimAndStake(uint256 amount, bytes32[] calldata merkleProof) external nonReentrant whenNotPaused {
        address user = msg.sender;
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

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L475-477)
```text
    function pause() external onlyOwner {
        _pause();
    }
```
