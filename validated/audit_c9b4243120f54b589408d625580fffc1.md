### Title
Unrestricted `claim()` Allows Anyone to Force-Claim on Behalf of Any User, Stealing Fee-Portion of Yield - (File: contracts/utils/MerkleDistributor/MerkleDistributor.sol)

---

### Summary

`MerkleDistributor.claim()` accepts an arbitrary `account` parameter but never verifies that `msg.sender == account`. Any external caller can trigger a claim for any user at any time, forcing the victim to pay the protocol fee on their claimable tokens. This is a direct analog to the external report's root cause: a claim function with user-controlled parameters that allows a third party to manipulate the claim outcome on behalf of another user.

---

### Finding Description

`MerkleDistributor.claim()` is a public, permissionless function that accepts `account` as a caller-supplied parameter:

```solidity
function claim(
    uint256 index,
    address account,
    uint256 cumulativeAmount,
    bytes32[] calldata merkleProof
) external override whenNotPaused {
```

There is no check of the form `require(msg.sender == account)` anywhere in the function body. The function proceeds to:

1. Verify the Merkle proof for `(index, account, cumulativeAmount)`.
2. Compute `claimableAmount = cumulativeAmount - userClaims[account].cumulativeAmount`.
3. Deduct a fee: `uint256 fee = (claimableAmount * feeInBPS) / 10_000`.
4. Transfer `amountToSend = claimableAmount - fee` to `account`.
5. Transfer `fee` to `protocolTreasury`.

The fee is permanently removed from the user's claimable balance. The attacker does not receive the fee — it goes to the treasury — but the user is robbed of the fee portion of their yield.

By contrast, `KernelMerkleDistributor._processClaim()` — a sibling contract in the same repository — explicitly enforces `if (account != msg.sender) { revert Unauthorized(); }`, demonstrating that the protocol is aware of this requirement and intentionally applied it there but omitted it from `MerkleDistributor`.

---

### Impact Explanation

**High — Theft of unclaimed yield.**

The fee parameter `feeInBPS` can be up to `MAX_FEE_IN_BPS = 1000` (10%). An attacker who force-claims for a victim causes the victim to permanently lose up to 10% of their claimable token balance to the protocol treasury. The victim receives fewer tokens than they are entitled to, with no recourse. This constitutes theft of unclaimed yield.

A particularly damaging scenario: the owner announces a fee reduction via `setFeeInBPS`. An attacker monitors the mempool and front-runs the fee reduction by calling `claim()` for every eligible user at the current high fee rate, maximizing the fee extracted from each victim before the reduction takes effect.

---

### Likelihood Explanation

**High.** The function is fully permissionless and requires only a valid Merkle proof, which is public off-chain data (typically published in a JSON file or IPFS). Any attacker can reconstruct valid proofs for any user from the published Merkle tree. No special privileges, capital, or complex setup are required. The attack is profitable whenever `feeInBPS > 0` and users have unclaimed balances.

---

### Recommendation

Add a `msg.sender == account` check at the top of `claim()`, mirroring the pattern already used in `KernelMerkleDistributor._processClaim()`:

```solidity
if (account != msg.sender) {
    revert Unauthorized();
}
```

Alternatively, remove the `account` parameter entirely and derive it from `msg.sender`, as done in `KernelTop100MerkleDistributor.claim()`.

---

### Proof of Concept

1. The Merkle tree for the current distribution is published off-chain. Attacker reads the leaf `(index=5, victim=0xVICTIM, cumulativeAmount=1000e18)` and its proof.
2. Current `feeInBPS = 500` (5%). Owner submits a transaction to call `setFeeInBPS(0)`.
3. Attacker front-runs with: `MerkleDistributor.claim(5, 0xVICTIM, 1000e18, proof)`.
4. The contract computes `claimableAmount = 1000e18`, `fee = 50e18`, `amountToSend = 950e18`.
5. `950e18` tokens are sent to `0xVICTIM`; `50e18` tokens are sent to `protocolTreasury`.
6. `userClaims[0xVICTIM].cumulativeAmount` is updated to `1000e18`.
7. The owner's `setFeeInBPS(0)` transaction executes, but the victim's claim is already consumed at the 5% fee rate.
8. The victim has permanently lost `50e18` tokens of yield they were entitled to receive in full.

**Root cause line:** [1](#0-0) 

**Fee deduction that harms the victim:** [2](#0-1) 

**Correct pattern (present in sibling contract, absent here):** [3](#0-2)

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

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L137-144)
```text
        // Send the claimable amount to the user - deducting the fee
        uint256 fee = (claimableAmount * feeInBPS) / 10_000;
        uint256 amountToSend = claimableAmount - fee;

        IERC20(token).safeTransfer(account, amountToSend);

        // Send the fee to the protocol treasury
        IERC20(token).safeTransfer(protocolTreasury, fee);
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L311-313)
```text
        if (account != msg.sender) {
            revert Unauthorized();
        }
```
