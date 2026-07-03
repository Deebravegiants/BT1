### Title
Updating `token` in `MerkleDistributor` Permanently Freezes Reward Claimants' Unclaimed Yield Due to Stale `cumulativeAmount` State - (File: `contracts/utils/MerkleDistributor/MerkleDistributor.sol`)

---

### Summary

`MerkleDistributor.sol` exposes a `setToken` admin function that replaces the distributed reward token address. However, the per-user `userClaims[account].cumulativeAmount` state — which is denominated in the **old** token's units — is never cleared. When a new merkle root is subsequently published for the new token, the claim logic subtracts the stale old-token `cumulativeAmount` from the new-token allocation, permanently freezing or under-paying every user who previously claimed.

---

### Finding Description

`MerkleDistributor` tracks each user's cumulative claim history in a single mapping:

```solidity
struct UserClaim {
    uint256 lastClaimedIndex;
    uint256 cumulativeAmount;   // denominated in the current token
}
mapping(address user => UserClaim userClaim) public userClaims;
``` [1](#0-0) 

The owner can replace the distributed token at any time:

```solidity
function setToken(address _token) external onlyOwner {
    if (_token == address(0)) revert ZeroValueProvided();
    token = _token;
    emit TokenUpdated(_token);
}
``` [2](#0-1) 

`setToken` does **not** reset `userClaims`. When the owner subsequently calls `setMerkleRoot` for the new token, `currentIndex` increments and a new root is active, but every user's `cumulativeAmount` still reflects their old-token history.

The claim path computes the payable delta as:

```solidity
uint256 claimableAmount = cumulativeAmount - userClaims[account].cumulativeAmount;
``` [3](#0-2) 

Because `userClaims[account].cumulativeAmount` is the old-token amount, not zero, the subtraction is wrong for the new token's distribution:

- If old-token `cumulativeAmount` ≥ new-token allocation → arithmetic underflow → revert → **complete freeze** of the user's new-token yield.
- If old-token `cumulativeAmount` < new-token allocation → user receives only the difference → **partial freeze** of new-token yield.

The `isClaimed` guard (`lastClaimedIndex >= index`) does not prevent this: a user who claimed at index 1 (old token) is not blocked from claiming at index 2 (new token), so the only broken gate is the `cumulativeAmount` subtraction. [4](#0-3) 

The `setMerkleRoot` function, which is the only state-advancing admin call, only increments `currentIndex` and replaces the root; it never touches `userClaims`: [5](#0-4) 

---

### Impact Explanation

Every user who claimed any amount of the old token will have their new-token claims permanently reduced or completely frozen. There is no recovery path: `userClaims` has no admin-reset function, and the contract is not re-deployable without losing all existing claim history. This constitutes **permanent freezing of unclaimed yield** for reward claimants.

Impact: **Medium** — Permanent freezing of unclaimed yield.

---

### Likelihood Explanation

`setToken` is explicitly designed to be called post-deployment (the `initialize` comment reads *"token can be set later"*), making a token update a planned, non-exceptional admin action. [6](#0-5) 

Any legitimate token migration (e.g., token contract upgrade, rebranding, or bug fix in the token) will trigger this bug for all users who have previously claimed. The likelihood is **Medium**: the action is explicitly supported and requires no compromise.

---

### Recommendation

When `setToken` is called to replace the distributed token, the contract must either:

1. **Reset all `userClaims`** — iterate or use a versioned mapping keyed by `(tokenEpoch, address)` so old-token history does not pollute new-token accounting; or
2. **Make `token` immutable** (set only at initialization, never updatable) — analogous to the fix applied in the referenced report where `QuestBoard` was made immutable; or
3. **Require a fresh deployment** for each new token, as the cumulative accounting model is inherently token-specific.

---

### Proof of Concept

**Setup:**
- `MerkleDistributor` is deployed with `tokenA`.
- Owner calls `setMerkleRoot(root1)` → `currentIndex = 1`.
- Alice calls `claim(1, alice, 500e18, proof)`:
  - `claimableAmount = 500e18 - 0 = 500e18` ✓
  - `userClaims[alice] = {lastClaimedIndex: 1, cumulativeAmount: 500e18}`

**Token update:**
- Owner calls `setToken(tokenB)` — `userClaims[alice].cumulativeAmount` remains `500e18`.
- Owner calls `setMerkleRoot(root2)` → `currentIndex = 2`.
- New merkle tree assigns Alice `300e18` of `tokenB` (cumulative).

**Alice attempts to claim `tokenB`:**
- `isClaimed(2, alice)` → `1 >= 2` → `false` (not blocked).
- `claimableAmount = 300e18 - 500e18` → **arithmetic underflow → revert**.
- Alice's entire `tokenB` allocation is permanently frozen.

**Variant (partial freeze):**
- If Alice's `tokenB` allocation is `600e18`:
  - `claimableAmount = 600e18 - 500e18 = 100e18` (Alice receives only `100e18` instead of `600e18`).
  - `500e18` of `tokenB` is permanently frozen with no recovery path. [7](#0-6)

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

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L125-135)
```text
        // Calculate the claimable amount
        uint256 claimableAmount = cumulativeAmount - userClaims[account].cumulativeAmount;

        // Ensure there is something to claim
        if (claimableAmount == 0) {
            revert NoTokensToClaim();
        }

        // Update user claim info, and send the token.
        userClaims[account].lastClaimedIndex = index;
        userClaims[account].cumulativeAmount = cumulativeAmount;
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L156-167)
```text
    function setMerkleRoot(bytes32 _merkleRootToSet) external onlyOwner {
        if (_merkleRootToSet == bytes32(0)) {
            revert ZeroValueProvided();
        }

        currentMerkleRoot = _merkleRootToSet;

        currentMerkleRootIndex++;
        currentIndex++;

        emit MerkleRootSet(currentMerkleRootIndex, currentMerkleRoot);
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
