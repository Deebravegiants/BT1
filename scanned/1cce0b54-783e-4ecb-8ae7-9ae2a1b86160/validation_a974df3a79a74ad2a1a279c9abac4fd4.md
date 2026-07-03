### Title
Missing `msg.sender == account` Validation Allows Forced Claims with Fee Theft — (`contracts/utils/MerkleDistributor/MerkleDistributor.sol`)

---

### Summary

`MerkleDistributor.claim` does not validate that `msg.sender == account`. Any unprivileged caller who possesses a valid merkle proof for a victim can trigger a claim on the victim's behalf. When a non-zero `feeInBPS` is configured, the fee is permanently deducted from the victim's allocation and sent to `protocolTreasury` — without the victim's consent. The sibling contract `KernelMerkleDistributor` explicitly guards against this with an `Unauthorized` revert, confirming the protocol is aware of the pattern but failed to apply it consistently.

---

### Finding Description

`MerkleDistributor.claim` accepts a caller-supplied `account` parameter and verifies a merkle proof for `(index, account, cumulativeAmount)`, but performs no check that the caller is the account being claimed for: [1](#0-0) 

The function transfers `amountToSend` to `account` and the fee to `protocolTreasury`: [2](#0-1) 

By contrast, `KernelMerkleDistributor._processClaim` explicitly enforces caller identity: [3](#0-2) 

The fee is configurable up to `MAX_FEE_IN_BPS = 1000` (10%): [4](#0-3) 

An attacker who obtains a victim's merkle proof (proofs are published off-chain for users to claim) calls `claim(index, victimAddress, cumulativeAmount, proof)`. The contract:
1. Verifies the proof — passes, because the proof is valid for `victimAddress`.
2. Computes `fee = claimableAmount * feeInBPS / 10_000` and deducts it.
3. Sends `amountToSend` to `victimAddress` and `fee` to `protocolTreasury`.

The victim permanently loses the fee portion of their allocation. The attacker pays only gas.

---

### Impact Explanation

**High — Theft of unclaimed yield.**

Every user whose merkle proof is known (i.e., all users, since proofs are distributed publicly) can be force-claimed at any time. At 10% maximum fee, up to 10% of every user's token allocation is permanently redirected to `protocolTreasury` without the user's consent. The victim cannot prevent this once the merkle root is set and their proof is public.

---

### Likelihood Explanation

**High.** Merkle proofs for distributor contracts are always published off-chain (otherwise users cannot claim). No special privilege, role, or capital is required. Any EOA can execute the attack for any victim in a single transaction.

---

### Recommendation

Add a caller-identity check at the top of `claim`, mirroring the pattern already used in `KernelMerkleDistributor`:

```solidity
if (account != msg.sender) {
    revert Unauthorized();
}
``` [5](#0-4) 

---

### Proof of Concept

1. Owner sets `feeInBPS = 1000` (10%) and publishes a merkle root.
2. Off-chain distribution publishes Alice's proof: `(index=1, account=Alice, cumulativeAmount=1000e18, proof=[...])`.
3. Attacker (Bob) calls:
   ```solidity
   merkleDistributor.claim(1, Alice, 1000e18, aliceProof);
   ```
4. Contract verifies proof — valid. Computes `fee = 100e18`, `amountToSend = 900e18`.
5. `900e18` tokens sent to Alice; `100e18` tokens sent to `protocolTreasury`.
6. Alice's `userClaims` is updated; she can never reclaim the 100e18 fee.
7. Bob spent only gas. Alice permanently lost 10% of her allocation.

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L47-47)
```text
    uint256 public constant MAX_FEE_IN_BPS = 1000;
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L97-123)
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
        if (currentMerkleRoot == bytes32(0)) {
            revert ZeroValueProvided();
        }

        if (index == 0 || index > currentIndex) {
            revert InvalidIndex();
        }

        if (isClaimed(index, account)) {
            revert AlreadyClaimed();
        }

        // Verify the merkle proof.
        bytes32 node = keccak256(abi.encodePacked(index, account, cumulativeAmount));
        if (!MerkleProofUpgradeable.verify(merkleProof, currentMerkleRoot, node)) {
            revert InvalidMerkleProof();
        }
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L137-145)
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
