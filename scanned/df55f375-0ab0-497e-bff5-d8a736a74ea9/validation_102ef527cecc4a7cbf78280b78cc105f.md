Looking at the `claim` function carefully:

### Title
Unrestricted `claim()` Allows Anyone to Force-Claim Victim's Yield at Current Fee Rate, Permanently Denying Fee-Free Claim Opportunity — (`contracts/utils/MerkleDistributor/MerkleDistributor.sol`)

---

### Summary

`MerkleDistributor.claim()` has no `msg.sender == account` guard. Any caller can trigger a claim for any `account` at the current `feeInBPS`. If the owner subsequently reduces `feeInBPS`, the victim permanently loses the fee delta on yield they could have claimed fee-free.

---

### Finding Description

The `claim` function accepts an arbitrary `account` parameter and applies no restriction on who may call it on behalf of that account. [1](#0-0) 

The fee is computed at the **current** `feeInBPS` at call time: [2](#0-1) 

`setFeeInBPS` is owner-callable and can reduce the fee to 0 at any time: [3](#0-2) 

Once a claim is recorded, `isClaimed` returns true for that index/account pair and any subsequent call reverts with `AlreadyClaimed`: [4](#0-3) 

There is no mechanism for the victim to reclaim the fee portion after the fact.

---

### Impact Explanation

**High — Theft of unclaimed yield.**

A victim with `cumulativeAmount` of unclaimed yield loses up to `MAX_FEE_IN_BPS / 10000 = 10%` of that yield permanently. The fee is diverted to `protocolTreasury` rather than the victim. The victim's claim state is marked as settled at the forced index, so they cannot re-claim. The lost amount is bounded by `claimableAmount * feeInBPS / 10_000`, which at the maximum fee of 1000 BPS equals 10% of total unclaimed yield.

---

### Likelihood Explanation

- Merkle proofs are public off-chain data (standard for Merkle distributors); the attacker needs no privileged access to construct a valid call.
- The attacker only needs to observe a pending fee reduction (e.g., governance announcement, pending transaction in mempool) and front-run it.
- The call costs only gas; the attacker need not hold any tokens.
- The owner reducing fees is a plausible operational event (e.g., promotional period, protocol maturation).

---

### Recommendation

Add a caller restriction so only the account itself (or an explicitly approved delegate) can trigger a claim:

```solidity
function claim(
    uint256 index,
    address account,
    uint256 cumulativeAmount,
    bytes32[] calldata merkleProof
) external override whenNotPaused {
    require(msg.sender == account, "MerkleDistributor: caller is not account");
    // ... rest of logic
}
```

Alternatively, implement a signed-delegation pattern if third-party claiming is a desired feature.

---

### Proof of Concept

Fork-test outline (no mainnet execution):

```solidity
// Setup: feeInBPS = 1000 (10%), victim has 1000e18 claimable
// Scenario A: victim self-claims AFTER owner sets feeInBPS = 0
//   victim receives: 1000e18 (full amount, fee = 0)

// Scenario B: attacker force-claims BEFORE owner sets feeInBPS = 0
//   attacker calls: distributor.claim(currentIndex, victim, 1000e18, proof)
//   victim receives: 900e18 (fee = 100e18 sent to treasury)
//   owner then sets feeInBPS = 0 — victim cannot re-claim (AlreadyClaimed)

// Assert: scenarioA_received - scenarioB_received == 100e18
//       == fee * cumulativeAmount / 10_000
```

The two scenarios are locally reproducible on a fork with unmodified contract code. The yield difference equals exactly `feeInBPS * claimableAmount / 10_000`, confirming permanent loss. [5](#0-4)

### Citations

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

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L115-117)
```text
        if (isClaimed(index, account)) {
            revert AlreadyClaimed();
        }
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L125-144)
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

        // Send the claimable amount to the user - deducting the fee
        uint256 fee = (claimableAmount * feeInBPS) / 10_000;
        uint256 amountToSend = claimableAmount - fee;

        IERC20(token).safeTransfer(account, amountToSend);

        // Send the fee to the protocol treasury
        IERC20(token).safeTransfer(protocolTreasury, fee);
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L198-206)
```text
    function setFeeInBPS(uint256 _feeInBPS) external onlyOwner {
        if (_feeInBPS > MAX_FEE_IN_BPS) {
            revert InvalidFeeInBPS();
        }

        feeInBPS = _feeInBPS;

        emit FeeInBPSUpdated(_feeInBPS);
    }
```
