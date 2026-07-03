### Title
Stale `cumulativeAmount` Across Token Changes Permanently Freezes User Yield Claims - (File: contracts/utils/MerkleDistributor/MerkleDistributor.sol)

---

### Summary

`MerkleDistributor.sol` maintains a single `userClaims[account].cumulativeAmount` that is never reset when the owner changes the distributed token via `setToken()`. When a new token with a different decimal scale is introduced and a new merkle root is published, every user who claimed in the prior distribution will have their new claim permanently revert due to an arithmetic underflow, freezing their unclaimed yield.

---

### Finding Description

`MerkleDistributor` is designed to support multiple sequential distribution rounds. The owner can change the distributed token at any time via `setToken()` and publish a fresh merkle root via `setMerkleRoot()`. [1](#0-0) 

Each time `setMerkleRoot()` is called, `currentIndex` increments, which allows users to claim again (the `isClaimed` guard only checks `lastClaimedIndex >= index`). [2](#0-1) 

However, the claimable amount is computed as:

```solidity
uint256 claimableAmount = cumulativeAmount - userClaims[account].cumulativeAmount;
``` [3](#0-2) 

`userClaims[account].cumulativeAmount` is never cleared when the token changes. It retains the raw token-unit value from the previous distribution. When the new token has fewer decimals (or when the new distribution simply starts cumulative amounts from zero for a fresh season), the subtraction underflows and reverts under Solidity 0.8's checked arithmetic, permanently blocking the user from claiming.

The `UserClaim` struct and its single shared mapping are the root cause: [4](#0-3) 

---

### Impact Explanation

**Medium — Permanent freezing of unclaimed yield.**

Every user who claimed in a prior distribution round is permanently unable to claim from any subsequent distribution whose new-token cumulative amounts are numerically smaller than the old-token amounts stored in `userClaims`. Their yield allocation exists in the merkle tree and in the contract's token balance, but the claim call always reverts. The funds are not stolen; they are frozen in the contract with no recovery path for affected users.

---

### Likelihood Explanation

The `initialize()` comment explicitly states "token can be set later", and `setToken()` is a first-class admin function, making token rotation a documented and expected operational pattern. [5](#0-4) 

Any token rotation from an 18-decimal token to a 6-decimal token (e.g., USDC, USDT) — or any fresh-season distribution that resets cumulative amounts — triggers the freeze for all prior claimants simultaneously. The likelihood is **medium**: it requires a routine admin action (token change + new merkle root), not an exploit, and the impact is protocol-wide for all prior claimants.

---

### Recommendation

When `setToken()` is called, reset all per-user `cumulativeAmount` values, or — more practically — store claimed amounts keyed by `(address user, address token)` or by `(address user, uint256 distributionEpoch)` so that each token/epoch has its own independent accounting. Alternatively, require that cumulative amounts in successive merkle roots for the same token are always monotonically increasing and prohibit token changes without a full state reset.

---

### Proof of Concept

1. Owner deploys `MerkleDistributor` with Token A (18 decimals) and publishes merkle root at `currentIndex = 1`.
2. Alice calls `claim(1, alice, 1000e18, proof)`. Her `userClaims[alice].cumulativeAmount` is now `1000e18` and `lastClaimedIndex = 1`. [6](#0-5) 
3. Owner calls `setToken(tokenB)` where Token B has 6 decimals.
4. Owner calls `setMerkleRoot(newRoot)` → `currentIndex` becomes `2`. The new merkle tree encodes Alice's cumulative allocation as `500e6` (500 Token B).
5. Alice calls `claim(2, alice, 500e6, proof)`.
6. Inside `claim()`: `claimableAmount = 500e6 - 1000e18`. Solidity 0.8 reverts on underflow. [7](#0-6) 
7. Alice's Token B yield is permanently frozen. There is no admin function to reset `userClaims[alice].cumulativeAmount`.

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L58-63)
```text
    struct UserClaim {
        uint256 lastClaimedIndex;
        uint256 cumulativeAmount;
    }

    mapping(address user => UserClaim userClaim) public userClaims;
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L71-72)
```text
    function initialize(address token_, address _protocolTreasury, uint256 _feeInBPS) external initializer {
        // token can be set later but not the protocol treasury
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L90-93)
```text
    function isClaimed(uint256 index, address account) public view override returns (bool) {
        if (index == 0) revert ZeroValueProvided();

        return userClaims[account].lastClaimedIndex >= index;
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L125-131)
```text
        // Calculate the claimable amount
        uint256 claimableAmount = cumulativeAmount - userClaims[account].cumulativeAmount;

        // Ensure there is something to claim
        if (claimableAmount == 0) {
            revert NoTokensToClaim();
        }
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L133-135)
```text
        // Update user claim info, and send the token.
        userClaims[account].lastClaimedIndex = index;
        userClaims[account].cumulativeAmount = cumulativeAmount;
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
