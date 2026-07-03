### Title
Fee Truncation to Zero via Integer Division Allows Fee-Free Claims — (`contracts/utils/MerkleDistributor/MerkleDistributor.sol`)

---

### Summary

The `claim` function computes the protocol fee using integer division: `fee = (claimableAmount * feeInBPS) / 10_000`. When `claimableAmount` is below the truncation threshold `10_000 / feeInBPS`, the fee rounds down to zero. Because there is no minimum-fee guard and no `if (fee > 0)` check before the treasury transfer, a claimer can receive the full `claimableAmount` while the treasury receives nothing.

---

### Finding Description

In `MerkleDistributor.claim`: [1](#0-0) 

```solidity
uint256 fee = (claimableAmount * feeInBPS) / 10_000;   // line 138 — truncates
uint256 amountToSend = claimableAmount - fee;

IERC20(token).safeTransfer(account, amountToSend);
// Send the fee to the protocol treasury
IERC20(token).safeTransfer(protocolTreasury, fee);     // line 144 — called even when fee == 0
```

The truncation threshold is `floor(10_000 / feeInBPS)`. For any `claimableAmount` strictly below this value, `fee` evaluates to `0` and the user receives the entire `claimableAmount`.

| `feeInBPS` | Threshold (wei) | Effective fee rate when `claimableAmount` = threshold − 1 |
|---|---|---|
| 1000 (10 %) | 10 | 0 % |
| 500 (5 %) | 20 | 0 % |
| 100 (1 %) | 100 | 0 % |
| 1 (0.01 %) | 10 000 | 0 % |

Contrast this with `KernelMerkleDistributor`, which wraps the treasury transfer in `if (fee > 0)` — an explicit acknowledgement that the zero-fee case must be handled: [2](#0-1) 

`MerkleDistributor` has no equivalent guard.

**Attack path (no Merkle forgery required):**

The Merkle root is updated by the owner via `setMerkleRoot`, which increments `currentIndex`. A claimer can call `claim` against every new index as soon as it is published, keeping each incremental `claimableAmount` as small as the per-period distribution for their address. If the per-period increment is below the truncation threshold, every individual claim pays zero fee. Waiting and claiming in bulk would pay the correct fee; claiming greedily at each root update avoids it entirely. [3](#0-2) 

The `isClaimed` check only prevents re-use of the same index; it does not prevent a user from claiming at index N, then index N+1, etc., each time with a small delta. [4](#0-3) 

---

### Impact Explanation

Every claim where `claimableAmount < 10_000 / feeInBPS` transfers the full amount to the user and zero to the treasury. Over many such claims the protocol collects no fees on that portion of the distribution. This is a direct, quantifiable loss of yield that should have accrued to the protocol treasury — matching the **High: Theft of unclaimed yield** scope.

---

### Likelihood Explanation

The condition is reachable whenever:
- The per-period Merkle increment for a user is below the truncation threshold, **or**
- A user deliberately claims at every root update rather than accumulating.

The second condition is entirely user-controlled and requires no special privileges. The first condition is common for small-balance holders or tokens with low decimal counts (e.g., 6-decimal tokens where the threshold for `feeInBPS = 1000` is 10 units = 0.00001 tokens — still reachable in practice). The `MAX_FEE_IN_BPS` cap of 1000 means the worst-case threshold is only 10 wei for 18-decimal tokens, but for lower-decimal tokens or low `feeInBPS` values the threshold grows substantially. [5](#0-4) 

---

### Recommendation

Add a minimum-fee enforcement or round-up the fee calculation:

```solidity
// Option A: round up
uint256 fee = feeInBPS > 0
    ? (claimableAmount * feeInBPS + 9_999) / 10_000
    : 0;

// Option B: enforce minimum of 1 when feeInBPS > 0 and claimableAmount > 0
if (feeInBPS > 0 && claimableAmount > 0 && fee == 0) {
    fee = 1;
}
```

Also add the `if (fee > 0)` guard before the treasury transfer (consistent with `KernelMerkleDistributor`) to avoid zero-value ERC20 transfers that may revert on non-standard tokens.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Fuzz: for all feeInBPS in [1, 1000] and claimableAmount in [1, 10_000/feeInBPS),
// assert fee > 0.
function testFeeNeverZero(uint256 feeInBPS, uint256 claimableAmount) public pure {
    feeInBPS = bound(feeInBPS, 1, 1000);
    // threshold: any value below this rounds to zero
    uint256 threshold = 10_000 / feeInBPS;
    claimableAmount = bound(claimableAmount, 1, threshold - 1);

    uint256 fee = (claimableAmount * feeInBPS) / 10_000;
    // This assertion FAILS — fee == 0 for all inputs in this range
    assert(fee > 0);
}
```

Running this Foundry fuzz test against the formula at line 138 will immediately find counterexamples (e.g., `feeInBPS = 999`, `claimableAmount = 1` → `fee = 0`), confirming the invariant is broken on unmodified production code. [6](#0-5)

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L47-47)
```text
    uint256 public constant MAX_FEE_IN_BPS = 1000;
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L90-94)
```text
    function isClaimed(uint256 index, address account) public view override returns (bool) {
        if (index == 0) revert ZeroValueProvided();

        return userClaims[account].lastClaimedIndex >= index;
    }
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

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L138-144)
```text
        uint256 fee = (claimableAmount * feeInBPS) / 10_000;
        uint256 amountToSend = claimableAmount - fee;

        IERC20(token).safeTransfer(account, amountToSend);

        // Send the fee to the protocol treasury
        IERC20(token).safeTransfer(protocolTreasury, fee);
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L341-343)
```text
        if (fee > 0) {
            kernel.safeTransfer(protocolTreasury, fee);
        }
```
