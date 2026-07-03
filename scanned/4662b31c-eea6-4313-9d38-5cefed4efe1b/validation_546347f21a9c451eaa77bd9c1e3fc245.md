### Title
Owner Can Drain KERNEL Token Balance Leaving `KernelTop100MerkleDistributor` Insolvent and Claimants Unable to Redeem Their Allocations - (File: contracts/KERNEL/KernelTop100MerkleDistributor.sol)

---

### Summary

`KernelTop100MerkleDistributor::withdrawTokens()` allows the owner to transfer any amount of any token — including the KERNEL distribution token itself — to an arbitrary recipient, with no check against the total outstanding claim liability. The contract holds KERNEL tokens that users are entitled to claim over a 30-day vesting schedule via Merkle proofs. Because no aggregate liability is tracked, the owner can drain the entire KERNEL balance, permanently preventing all pending claimants from receiving their entitled allocations.

---

### Finding Description

`KernelTop100MerkleDistributor` is funded with KERNEL tokens. Each user's total claimable allocation is encoded in a Merkle tree. Users call `claim()` or `claimAndStake()` to receive their vested portion over a 30-day window. The contract tracks per-user claimed amounts in `userClaims[user].amountClaimed`, but it does **not** track the aggregate total outstanding liability — i.e., the sum of all unclaimed allocations across all Merkle-eligible users.

The admin function `withdrawTokens()` at line 461 performs no solvency check:

```solidity
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

The only guards are: non-zero token address, non-zero recipient, non-zero amount. There is no check that `_amount` does not exceed `balance - totalOutstandingLiability`. The owner can pass `_token = address(kernel)` and `_amount = kernel.balanceOf(address(this))` to drain the entire KERNEL reserve in a single call. [1](#0-0) 

The vesting and claim logic correctly tracks per-user state: [2](#0-1) 

But there is no contract-level variable accumulating total unclaimed liability that `withdrawTokens` could be checked against. [3](#0-2) 

---

### Impact Explanation

**High — Theft of unclaimed yield.**

KERNEL tokens held by this contract represent yield/reward allocations owed to the top-100 eligible users. If the owner calls `withdrawTokens` with the KERNEL token address and the full contract balance, every pending claimant loses their entire unclaimed allocation. The `claim()` and `claimAndStake()` calls will revert on the `safeTransfer` due to zero balance, permanently freezing all outstanding yield. [4](#0-3) 

---

### Likelihood Explanation

The function is callable by the owner at any time with no timelock, no multi-sig requirement enforced at the contract level, and no on-chain delay. The design flaw is structural: the function is intended to recover mistakenly sent tokens or withdraw surplus, but it provides no enforcement of the invariant that the KERNEL balance must always cover outstanding claims. Any owner key compromise, or a malicious upgrade of the owner address, immediately enables a full drain. The absence of a surplus-only guard means the risk is present throughout the entire vesting period (30 days after `vestingStartTimestamp`). [5](#0-4) 

---

### Recommendation

Track the total outstanding KERNEL liability as a state variable. Increase it when the Merkle root is set (by the sum of all allocations) and decrease it as users claim. In `withdrawTokens`, when `_token == address(kernel)`, enforce:

```solidity
uint256 surplus = kernel.balanceOf(address(this)) - totalOutstandingLiability;
require(_amount <= surplus, "Insufficient surplus");
```

Alternatively, restrict `withdrawTokens` so it explicitly reverts when `_token == address(kernel)`, and provide a separate `withdrawSurplusKernel()` function that computes and enforces the surplus bound.

---

### Proof of Concept

1. The contract is deployed and funded with 1,000,000 KERNEL tokens for distribution to 100 users.
2. The Merkle root encodes 10,000 KERNEL per user (1,000,000 total liability).
3. Vesting begins; users start claiming their vested portions.
4. Owner calls:
   ```solidity
   withdrawTokens(address(kernel), kernel.balanceOf(address(this)), ownerAddress);
   ```
5. All remaining KERNEL tokens are transferred to the owner.
6. Any subsequent call to `claim()` or `claimAndStake()` by any user reverts because `kernel.safeTransfer(user, amountToSend)` fails — the contract holds zero KERNEL.
7. All unclaimed KERNEL allocations are permanently lost to users. [1](#0-0) [6](#0-5)

### Citations

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L127-127)
```text
    uint256 public constant VESTING_DURATION = 30 days;
```

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L152-158)
```text
    struct UserClaim {
        uint256 lastClaimTimestamp;
        uint256 amountClaimed;
    }

    /// @notice The user claims mapping
    mapping(address user => UserClaim userClaim) public userClaims;
```

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L235-273)
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
    }
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
