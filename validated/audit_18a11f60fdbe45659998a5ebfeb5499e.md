### Title
`MerkleDistributor.setToken` Updates Reward Token Without Distributing Pending Claims - (`contracts/utils/MerkleDistributor/MerkleDistributor.sol`)

### Summary
The `MerkleDistributor` contract exposes a `setToken` function that allows the owner to replace the reward token address at any time, without first ensuring all pending Merkle-tree claims against the old token have been distributed. This is the direct structural analog of the Sablier stream-update vulnerability: a state variable pointing to the reward source is overwritten while an unrecovered balance remains in the contract, permanently stranding those tokens.

### Finding Description
`setToken` (lines 185–193) unconditionally overwrites the `token` state variable:

```solidity
function setToken(address _token) external onlyOwner {
    if (_token == address(0)) {
        revert ZeroValueProvided();
    }
    token = _token;          // ← no check for outstanding claimable balance
    emit TokenUpdated(_token);
}
```

The `claim` function (standard MerkleDistributor pattern) reads `token` at execution time to perform the ERC-20 transfer to the claimant. Once `token` is replaced:

1. The old token balance already held by the contract is no longer reachable through any claim path — every future `claim` call will attempt to transfer the **new** token.
2. Users who had not yet claimed their allocation against the old Merkle root lose access to those funds permanently (or until an out-of-band admin rescue, which is not guaranteed).
3. If the new token is not pre-funded in the contract, all subsequent claims revert, freezing the entire distribution.

The root cause is identical to the Sablier report: a pointer to the reward source (`_stream` / `token`) is updated without first draining the pending balance that was accumulated under the old pointer.

### Impact Explanation
- **Permanent freezing of unclaimed yield** (Medium): all users who have not yet submitted their Merkle proof lose access to their earned rewards denominated in the old token.
- Escalates to **theft of unclaimed yield** (High) if the stranded old-token balance is later recovered by the owner via an emergency-withdraw path and not redistributed to rightful claimants.

### Likelihood Explanation
Token migrations are a realistic operational event (e.g., upgrading a reward token, switching from one LST reward to another). The owner role may be a multi-sig or governance contract, introducing a window between the decision to migrate and the actual execution — during which new users may stake and earn claims against the old token that they have not yet claimed. The external report's sponsor confirmed an analogous governance delay scenario as realistic.

### Recommendation
1. Before overwriting `token`, check that the contract holds zero balance of the current token (i.e., all claims have been distributed):
   ```solidity
   require(IERC20(token).balanceOf(address(this)) == 0, "Pending claims exist");
   ```
2. Alternatively, snapshot and distribute all remaining old-token balance to claimants before the token switch, or pause claims and force a full distribution cycle first.
3. Emit the old token address in the event so off-chain monitors can detect and act on stranded balances.

### Proof of Concept
1. Admin calls `notifyRewardAmount` / funds the `MerkleDistributor` with 1 000 000 TOKEN\_A and sets a Merkle root covering 100 users.
2. 60 users claim; 40 users have not yet claimed (400 000 TOKEN\_A still in contract).
3. Admin calls `setToken(TOKEN_B)` (legitimate migration).
4. The 40 remaining users call `claim` — the function now calls `IERC20(TOKEN_B).transfer(...)`. If TOKEN\_B is not funded, every call reverts. The 400 000 TOKEN\_A is permanently stranded.
5. Even if TOKEN\_B is funded, the 400 000 TOKEN\_A sitting in the contract is inaccessible through any user-facing path. [1](#0-0)

### Citations

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
