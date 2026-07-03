### Title
Blacklisted `protocolTreasury` Permanently Freezes All Users' Unclaimed Yield in `MerkleDistributor.claim` - (File: contracts/utils/MerkleDistributor/MerkleDistributor.sol)

---

### Summary
`MerkleDistributor.claim` atomically pushes tokens to two addresses in the same transaction: the claimant (`account`) and the `protocolTreasury` (fee). If the distributed token is a blacklistable asset (e.g., USDC) and `protocolTreasury` is blacklisted, every user's `claim` call reverts, permanently freezing all unclaimed yield in the contract.

---

### Finding Description
The `claim` function in `MerkleDistributor` performs two sequential `safeTransfer` calls within a single atomic transaction:

```solidity
// Line 141
IERC20(token).safeTransfer(account, amountToSend);

// Line 144
IERC20(token).safeTransfer(protocolTreasury, fee);
``` [1](#0-0) 

The `token` address is fully configurable by the owner via `setToken`, meaning any ERC20 — including USDC — can be set as the distributed token. [2](#0-1) 

USDC (and USDT) implement an address blacklist. If `protocolTreasury` is blacklisted by the token issuer, the second `safeTransfer` on line 144 reverts. Because both transfers are in the same transaction with no try/catch, the entire `claim` call reverts. There is no alternative path for users to retrieve their tokens.

The `protocolTreasury` address is set at initialization and can only be changed by the owner: [3](#0-2) 

Until the owner updates `protocolTreasury` to a non-blacklisted address, **no user can claim any rewards** — the entire distributor is bricked.

A secondary (per-user) variant exists: if the `account` itself is blacklisted, the first `safeTransfer` on line 141 reverts, permanently freezing that individual user's unclaimed yield. [4](#0-3) 

---

### Impact Explanation
**Permanent freezing of unclaimed yield (Medium).**

- If `protocolTreasury` is blacklisted: 100% of users are unable to claim; all yield held in the contract is frozen until the owner intervenes by calling `setProtocolTreasury`.
- If a specific `account` is blacklisted: that user's entire unclaimed allocation is permanently frozen with no recovery path (no alternative recipient, no admin rescue for individual users).

---

### Likelihood Explanation
- `MerkleDistributor` is a generic contract whose `token` is explicitly settable to any ERC20, including USDC.
- USDC blacklisting of protocol-controlled addresses (e.g., treasury multisigs) has occurred historically due to regulatory or compliance actions.
- The `protocolTreasury` is a single point of failure: one blacklisting event affects every pending claimant simultaneously.
- Individual user blacklisting is a realistic scenario for any user who interacts with regulated stablecoins.

---

### Recommendation
1. **Accumulate fees internally** rather than pushing them to `protocolTreasury` on every claim. Add a separate `withdrawFees()` function that the treasury pulls from.
2. **Guard the fee transfer**: wrap it in a conditional so that if `fee == 0` or the transfer fails, the user's portion is still delivered.
3. **Separate the two transfers** so a failure on the fee leg does not block the user's claim.

Example pattern:
```solidity
// Accumulate fee internally
accruedFees += fee;
// Only transfer to user
IERC20(token).safeTransfer(account, amountToSend);

// Separate admin function
function withdrawFees(address recipient) external onlyOwner {
    uint256 amount = accruedFees;
    accruedFees = 0;
    IERC20(token).safeTransfer(recipient, amount);
}
```

---

### Proof of Concept
1. Owner deploys `MerkleDistributor` with `token = USDC`, `protocolTreasury = 0xTreasury`, `feeInBPS = 500` (5%).
2. A merkle root is posted; multiple users are eligible to claim.
3. USDC's issuer blacklists `0xTreasury` (e.g., regulatory action).
4. Any user calls `claim(index, account, cumulativeAmount, proof)`.
5. Execution reaches line 144: `IERC20(token).safeTransfer(protocolTreasury, fee)` → USDC reverts because `protocolTreasury` is blacklisted.
6. The entire transaction reverts. The user's state update (lines 134–135) is also rolled back, so the claim is not marked as used.
7. Every subsequent `claim` call by any user hits the same revert. All unclaimed yield is frozen until the owner calls `setProtocolTreasury` with a non-blacklisted address. [5](#0-4)

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L133-146)
```text
        // Update user claim info, and send the token.
        userClaims[account].lastClaimedIndex = index;
        userClaims[account].cumulativeAmount = cumulativeAmount;

        // Send the claimable amount to the user - deducting the fee
        uint256 fee = (claimableAmount * feeInBPS) / 10_000;
        uint256 amountToSend = claimableAmount - fee;

        IERC20(token).safeTransfer(account, amountToSend);

        // Send the fee to the protocol treasury
        IERC20(token).safeTransfer(protocolTreasury, fee);

        emit Claimed(index, account, claimableAmount);
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L169-180)
```text
    /// @dev Set the protocol treasury address.
    /// @dev only called by the owner.
    /// @param _protocolTreasury The address of the protocol treasury.
    function setProtocolTreasury(address _protocolTreasury) external onlyOwner {
        if (_protocolTreasury == address(0)) {
            revert ZeroValueProvided();
        }

        protocolTreasury = _protocolTreasury;

        emit ProtocolTreasuryUpdated(_protocolTreasury);
    }
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L185-193)
```text
    function setToken(address _token) external onlyOwner {
        if (_token == address(0)) {
            revert ZeroValueProvided();
        }

        token = _token;

        emit TokenUpdated(_token);
    }
```
