### Title
Missing `msg.sender == account` Authorization in `MerkleDistributor.claim` Allows Forced Claims, Stealing User Yield via Fee — (`contracts/utils/MerkleDistributor/MerkleDistributor.sol`)

---

### Summary

The `claim` function in `MerkleDistributor.sol` accepts an arbitrary `account` parameter but never verifies that `msg.sender == account`. Any external caller who possesses a valid Merkle proof for a victim can force-execute a claim on the victim's behalf at the current fee rate, permanently consuming the victim's claimable allocation and transferring the fee to the treasury — yield the victim can never recover.

---

### Finding Description

`MerkleDistributor.claim` is a public, permissionless function:

```solidity
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
``` [1](#0-0) 

The function verifies the Merkle proof, calculates the claimable delta, deducts a fee, and transfers the net amount to `account`:

```solidity
uint256 fee = (claimableAmount * feeInBPS) / 10_000;
uint256 amountToSend = claimableAmount - fee;

IERC20(token).safeTransfer(account, amountToSend);
IERC20(token).safeTransfer(protocolTreasury, fee);
``` [2](#0-1) 

There is **no check** that `msg.sender == account`. Merkle proofs are published off-chain (IPFS / protocol frontend) and are fully public. Any caller can supply a victim's `(index, account, cumulativeAmount, merkleProof)` tuple and trigger the claim.

By contrast, the sibling contract `KernelMerkleDistributor._processClaim` explicitly enforces this invariant:

```solidity
if (account != msg.sender) {
    revert Unauthorized();
}
``` [3](#0-2) 

`MerkleDistributor.sol` is a standalone deployable contract (not a base class for `KernelMerkleDistributor`) used for generic ERC-20 token distributions. [4](#0-3) 

---

### Impact Explanation

**Impact: High — Theft of unclaimed yield.**

The fee (`feeInBPS`, up to `MAX_FEE_IN_BPS = 1000`, i.e. 10%) is deducted from the victim's claimable allocation and sent to `protocolTreasury`. Once a forced claim executes, `userClaims[account].cumulativeAmount` is updated to the full `cumulativeAmount`:

```solidity
userClaims[account].lastClaimedIndex = index;
userClaims[account].cumulativeAmount = cumulativeAmount;
``` [5](#0-4) 

The victim can never re-claim the same allocation. If the victim intended to wait until `feeInBPS` was reduced to zero (a legitimate owner action via `setFeeInBPS`), the forced claim permanently destroys up to 10% of their yield. The attacker pays only gas; the stolen yield flows to the treasury, not the attacker — but the victim's loss is real and irreversible.

---

### Likelihood Explanation

**Likelihood: Medium.**

1. Merkle proofs for all eligible accounts are published publicly (standard practice for all Merkle airdrop/distribution deployments).
2. The call requires no special role, no capital, and no flash loan — only knowledge of the victim's proof tuple.
3. A rational griefing scenario exists: a competitor, a disgruntled user, or a bot can sweep all pending claims the moment `feeInBPS > 0`, forcing every holder to pay the maximum fee before any fee reduction takes effect.
4. The owner can set `feeInBPS` up to 1000 BPS (10%) at any time via `setFeeInBPS`. [6](#0-5) 

---

### Recommendation

Add a caller authorization check at the top of `claim`, mirroring the pattern already used in `KernelMerkleDistributor`:

```solidity
if (account != msg.sender) revert Unauthorized();
```

Alternatively, remove the `account` parameter entirely and derive it from `msg.sender`, as `KernelTop100MerkleDistributor` does. [7](#0-6) 

---

### Proof of Concept

1. Owner deploys `MerkleDistributor` with `feeInBPS = 500` (5%).
2. Alice has a valid allocation of 1,000 tokens; her `(index, address, cumulativeAmount, proof)` tuple is published on the protocol's distribution page.
3. Alice decides to wait, expecting the owner to call `setFeeInBPS(0)` next week.
4. Bob (attacker) calls `claim(index, alice, 1000e18, proof)` before the fee reduction.
5. Alice receives 950 tokens; 50 tokens (5%) are sent to `protocolTreasury`.
6. `userClaims[alice].cumulativeAmount` is now set to 1000e18 — Alice can never reclaim the 50 tokens.
7. When the owner later sets `feeInBPS = 0`, Alice has nothing left to claim.

Alice permanently loses 50 tokens of yield she would have received in full had she been allowed to choose her own claim timing.

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L44-51)
```text
contract MerkleDistributor is IMerkleDistributor, OwnableUpgradeable, PausableUpgradeable {
    using SafeERC20 for IERC20;

    uint256 public constant MAX_FEE_IN_BPS = 1000;

    address public override token;
    address public protocolTreasury;
    uint256 public feeInBPS;
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

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L134-135)
```text
        userClaims[account].lastClaimedIndex = index;
        userClaims[account].cumulativeAmount = cumulativeAmount;
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L138-144)
```text
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

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L311-313)
```text
        if (account != msg.sender) {
            revert Unauthorized();
        }
```

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L310-311)
```text
    function claim(uint256 amount, bytes32[] calldata merkleProof) external nonReentrant whenNotPaused {
        address user = msg.sender;
```
