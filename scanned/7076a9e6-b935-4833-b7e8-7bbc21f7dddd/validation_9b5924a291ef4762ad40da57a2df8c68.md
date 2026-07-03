### Title
Reward Token Substitution in `MerkleDistributor` Allows Selective Yield Extraction - (File: contracts/utils/MerkleDistributor/MerkleDistributor.sol)

### Summary
`MerkleDistributor.sol` exposes a `setToken()` admin function that replaces the distributed ERC20 token at any time, with no snapshot or migration of already-accrued but unclaimed balances. Because the cumulative-claim accounting (`userClaims[account].cumulativeAmount`) is token-agnostic, a token switch mid-distribution gives every user a free option: claim the old token before the switch if it is more valuable, or wait and claim the new token if it is more valuable. This is the direct analog of the Yield "rewards squatting" finding.

### Finding Description
`MerkleDistributor.setToken()` unconditionally overwrites the `token` state variable:

```solidity
// contracts/utils/MerkleDistributor/MerkleDistributor.sol
function setToken(address _token) external onlyOwner {
    if (_token == address(0)) {
        revert ZeroValueProvided();
    }
    token = _token;          // ← replaces token with no accounting migration
    emit TokenUpdated(_token);
}
```

The `claim()` function then transfers whatever `token` currently points to:

```solidity
IERC20(token).safeTransfer(account, amountToSend);
```

User claim state is tracked only as a cumulative numeric amount:

```solidity
struct UserClaim {
    uint256 lastClaimedIndex;
    uint256 cumulativeAmount;   // ← no token address recorded
}
```

There is no record of which token a user's `cumulativeAmount` was denominated in. After `setToken()` is called, every subsequent `claim()` call transfers the new token using the old cumulative-amount arithmetic. Users who have not yet claimed hold a free option: they can observe the pending `setToken()` transaction in the mempool and choose to claim before or after the switch depending on which token is worth more.

### Impact Explanation
**High — Theft of unclaimed yield.**

Scenario A (new token is less valuable): A user front-runs `setToken(tokenB)` by calling `claim()` while `token == tokenA`. They receive the more valuable `tokenA`. Users who do not front-run receive the less valuable `tokenB` for the same merkle-tree amount, losing yield.

Scenario B (new token is more valuable): Users who have not yet claimed simply wait until after `setToken(tokenB)` executes and then call `claim()`, receiving `tokenB` at the same numeric amount that was denominated in `tokenA`. The protocol distributes more economic value than intended.

In both scenarios the asymmetric option is entirely free to the user and is a direct consequence of the missing per-claim token snapshot.

### Likelihood Explanation
**Medium.** The owner must call `setToken()` for the attack to be possible, but `setToken()` is an explicitly provided, unrestricted admin function with no time-lock or migration guard. Any future token rotation (e.g., switching from a points token to a live ERC20, or rotating reward tokens across distribution epochs) triggers the vulnerability. Mempool monitoring is trivial and widely practiced by MEV searchers.

### Recommendation
1. Remove `setToken()` entirely and require a new distributor deployment for each token, as done in `KernelMerkleDistributor.sol` (which fixes the token at initialization and provides no setter).
2. If token rotation is required, record the token address inside `UserClaim` and settle outstanding balances in the old token before activating the new one, or use a per-epoch index mapping (as suggested in the original Yield report).

### Proof of Concept
```
State: MerkleDistributor deployed with token = DAI ($1).
       Merkle root encodes: Alice → cumulativeAmount = 1000.
       Alice has not yet claimed.

Step 1: Owner broadcasts setToken(WETH) where WETH = $3000.
Step 2: Alice sees the pending tx in the mempool.
        If she prefers DAI: she front-runs with claim(index, alice, 1000, proof)
          → receives 1000 DAI ($1000).
        If she prefers WETH: she waits until setToken confirms, then calls claim()
          → receives 1000 WETH ($3,000,000).

Either way Alice holds a costless option over which token she receives,
at the expense of the protocol or other claimants.
```

**Root cause lines:** [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L58-63)
```text
    struct UserClaim {
        uint256 lastClaimedIndex;
        uint256 cumulativeAmount;
    }

    mapping(address user => UserClaim userClaim) public userClaims;
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L126-141)
```text
        uint256 claimableAmount = cumulativeAmount - userClaims[account].cumulativeAmount;

        // Ensure there is something to claim
        if (claimableAmount == 0) {
            revert NoTokensToClaim();
        }

        // Update user claim info, and send the token.
        userClaims[account].lastClaimedIndex = index;
        userClaims[account].cumulativeAmount = cumulativeAmount;

        // Send the claimable amount to the user - deducting the fee
        uint256 fee = (claimableAmount * feeInBPS) / 10_000;
        uint256 amountToSend = claimableAmount - fee;

        IERC20(token).safeTransfer(account, amountToSend);
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
