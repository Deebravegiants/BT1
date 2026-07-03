### Title
Unprivileged Caller Can Force Claim on Behalf of Any Account, Extracting Protocol Fee from Victim's Unclaimed Yield — (File: `contracts/utils/MerkleDistributor/MerkleDistributor.sol`)

---

### Summary

`MerkleDistributor.claim()` contains no `msg.sender == account` guard. Any address can supply a valid merkle proof (which is public data) and trigger a claim for an arbitrary victim, forcing immediate fee deduction at whatever `feeInBPS` is currently set — up to 10% of the victim's claimable amount — routed to `protocolTreasury` without the victim's consent.

---

### Finding Description

The `claim` function signature is:

```solidity
function claim(
    uint256 index,
    address account,
    uint256 cumulativeAmount,
    bytes32[] calldata merkleProof
) external override whenNotPaused
``` [1](#0-0) 

The only guards present are:
- `whenNotPaused`
- `currentMerkleRoot != bytes32(0)`
- `index` range check
- `isClaimed` replay check
- Merkle proof validity

There is **no check** that `msg.sender == account`. After proof verification, the fee is computed and deducted unconditionally:

```solidity
uint256 fee = (claimableAmount * feeInBPS) / 10_000;
uint256 amountToSend = claimableAmount - fee;

IERC20(token).safeTransfer(account, amountToSend);
IERC20(token).safeTransfer(protocolTreasury, fee);
``` [2](#0-1) 

The maximum fee is enforced at `MAX_FEE_IN_BPS = 1000` (10%): [3](#0-2) 

---

### Impact Explanation

When `feeInBPS = 1000`:

- Victim has `claimableAmount = X` tokens of unclaimed yield.
- Attacker calls `claim(index, victim, X, proof)`.
- Victim receives `0.9 * X`; `0.1 * X` is permanently transferred to `protocolTreasury`.
- Victim loses 10% of their yield with no recourse.

A victim may have been deliberately deferring their claim waiting for the owner to reduce `feeInBPS` (which is mutable via `setFeeInBPS`). The forced claim locks in the maximum fee before any reduction occurs. The victim's yield is permanently reduced — this is **theft of unclaimed yield**.

---

### Likelihood Explanation

- Merkle proofs are public: the distributor's merkle tree data is published off-chain so users can construct their own proofs. Any observer can reconstruct `(index, account, cumulativeAmount, proof)` for any leaf.
- No special role, key, or privileged access is required.
- The attack is a single permissionless transaction.
- Likelihood is **High**.

---

### Recommendation

Add a caller restriction to `claim`:

```solidity
function claim(
    uint256 index,
    address account,
    uint256 cumulativeAmount,
    bytes32[] calldata merkleProof
) external override whenNotPaused {
    require(msg.sender == account, "MerkleDistributor: caller is not the account");
    // ...
}
```

This ensures only the beneficiary can trigger their own claim, preserving their right to time the claim relative to the current `feeInBPS`.

---

### Proof of Concept

```solidity
// Setup: feeInBPS = 1000 (10%), victim has valid unclaimed leaf
// Attacker (any EOA) executes:
merkleDistributor.claim(
    victimIndex,
    victimAddress,
    victimCumulativeAmount,
    victimMerkleProof   // obtained from published merkle tree
);

// Result:
// victim receives: victimCumulativeAmount * 90% (not 100%)
// protocolTreasury receives: victimCumulativeAmount * 10%
// attacker spent only gas; victim lost 10% of yield without consent
assertEq(
    token.balanceOf(victimAddress),
    victimCumulativeAmount * 9000 / 10_000
);
```

The root cause is the missing `msg.sender == account` check at [1](#0-0) , combined with the unconditional fee deduction at [2](#0-1) .

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L47-47)
```text
    uint256 public constant MAX_FEE_IN_BPS = 1000;
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L97-106)
```text
    function claim(
        uint256 index,
        address account,
        uint256 cumulativeAmount,
        bytes32[] calldata merkleProof
    )
        external
        override
        whenNotPaused
    {
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L138-144)
```text
        uint256 fee = (claimableAmount * feeInBPS) / 10_000;
        uint256 amountToSend = claimableAmount - fee;

        IERC20(token).safeTransfer(account, amountToSend);

        // Send the fee to the protocol treasury
        IERC20(token).safeTransfer(protocolTreasury, fee);
```
