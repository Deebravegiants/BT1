The `withdrawTokens` function at line 461 has been fully read. Let me confirm the complete guard set:

- `onlyOwner` modifier
- `checkNonZeroAddress(_token)` and `checkNonZeroAddress(_recipient)`
- `_amount == 0` revert

There is **no guard** that:
- Prevents `_token == address(kernel)` (the distribution token)
- Checks remaining user allocations or contract solvency
- Enforces any time-lock relative to `vestingStartTimestamp + VESTING_DURATION`

The path is concrete and unambiguous.

---

### Title
Owner Can Drain KERNEL Distribution Balance via Unrestricted `withdrawTokens`, Stealing All Unclaimed Yield — (`contracts/KERNEL/KernelTop100MerkleDistributor.sol`)

### Summary
`KernelTop100MerkleDistributor.withdrawTokens` imposes no restriction on withdrawing the contract's own KERNEL distribution token. The owner can call it at any time, for any amount, draining the entire balance that backs user merkle allocations.

### Finding Description
`withdrawTokens` is a generic token-rescue function with only three guards: `onlyOwner`, non-zero address, and non-zero amount. [1](#0-0) 

It accepts an arbitrary `_token` address and transfers `_amount` to `_recipient` with no check that `_token != address(kernel)`, no check against the aggregate merkle-allocated balance, and no time constraint relative to `vestingStartTimestamp` or `VESTING_DURATION`. [2](#0-1) 

The vesting schedule in `_getUnclaimedVestedAmount` computes claimable amounts purely from `block.timestamp` and `userClaims` state — it has no awareness of whether the contract actually holds sufficient KERNEL to satisfy those amounts. [3](#0-2) 

### Impact Explanation
The owner can call `withdrawTokens(address(kernel), kernel.balanceOf(address(this)), recipient)` at any point — before, during, or after the vesting window — and transfer the entire KERNEL balance out of the contract. Every subsequent `claim` or `claimAndStake` call by a merkle-eligible user will revert with an ERC-20 insufficient-balance error. All unclaimed yield across every eligible user is permanently unrecoverable from this distributor instance. Multiple deployed instances exist on mainnet (May 2025, Jun 2025, Season 2, July 14, August 14, Sep 14 vesting). [1](#0-0) 

### Likelihood Explanation
The call requires only the owner key. No time-lock, no multi-sig requirement, no on-chain delay is enforced by the contract itself. The owner is a single EOA or a proxy admin; if that key is compromised or acts adversarially, the attack is a single transaction. Given multiple live deployments, the aggregate at-risk balance is material.

### Recommendation
Add a guard in `withdrawTokens` that prevents withdrawal of the KERNEL distribution token entirely, or alternatively track the total merkle-allocated amount at initialization and only allow withdrawal of `kernel.balanceOf(address(this)) - totalAllocated` (i.e., excess tokens only). Example minimal fix:

```solidity
function withdrawTokens(address _token, uint256 _amount, address _recipient) external onlyOwner {
    if (_token == address(kernel)) revert CannotWithdrawDistributionToken();
    // ... existing checks
}
```

### Proof of Concept
```solidity
// 1. Deploy KernelTop100MerkleDistributor with merkleRoot covering N users,
//    fund with N * amount KERNEL, vestingStartTimestamp = block.timestamp + 1 day.
// 2. Warp past vestingStartTimestamp so users have non-zero getClaimableAmount.
// 3. Owner calls:
distributor.withdrawTokens(address(kernel), kernel.balanceOf(address(distributor)), owner);
// 4. Assert:
assert(kernel.balanceOf(address(distributor)) == 0);
// 5. Any user attempts to claim:
vm.expectRevert(); // ERC20: transfer amount exceeds balance
distributor.claim(userAmount, proof);
// getClaimableAmount still returns non-zero — tokens are gone.
``` [4](#0-3)

### Citations

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L127-127)
```text
    uint256 public constant VESTING_DURATION = 30 days;
```

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L235-272)
```text
    function _getUnclaimedVestedAmount(address user, uint256 userTotalClaimableAmount) internal view returns (uint256) {
        UserClaim storage userClaim = userClaims[user];

        // If user has claimed everything, return 0
        if (userClaim.amountClaimed >= userTotalClaimableAmount) {
            return 0;
        }

        // Calculate vesting end time
        uint256 vestingEndTime = vestingStartTimestamp + VESTING_DURATION;

        // Calculate start and end times for the period
        uint256 startTime = userClaim.lastClaimTimestamp > 0 ? userClaim.lastClaimTimestamp : vestingStartTimestamp;

        // Cap current time at vesting end time
        uint256 currentTime = block.timestamp;
        if (currentTime > vestingEndTime) {
            currentTime = vestingEndTime;
        }

        // If current time is before start time or vesting hasn't started yet, nothing to claim
        if (currentTime <= startTime || currentTime <= vestingStartTimestamp) {
            return 0;
        }

        // Calculate total vested amount based on time elapsed since vesting start
        uint256 totalElapsedTime = currentTime - vestingStartTimestamp;
        uint256 totalVestedAmount = (userTotalClaimableAmount * totalElapsedTime) / VESTING_DURATION;

        // Cap at total amount
        if (totalVestedAmount > userTotalClaimableAmount) {
            totalVestedAmount = userTotalClaimableAmount;
        }

        // Calculate unclaimed amount
        uint256 unclaimedAmount = totalVestedAmount - userClaim.amountClaimed;

        return unclaimedAmount;
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
