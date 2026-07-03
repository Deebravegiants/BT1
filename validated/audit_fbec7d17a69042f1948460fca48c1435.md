### Title
`KernelMerkleDistributor.claim()` wrongly restricts caller to the beneficiary account - (File: contracts/KERNEL/KernelMerkleDistributor.sol)

### Summary

`KernelMerkleDistributor._processClaim()` contains an `account != msg.sender` guard that prevents any third party from submitting a valid merkle proof on behalf of a beneficiary. The function signature accepts an explicit `account` parameter — exactly the design pattern used to allow permissionless, proof-gated claiming — yet the guard silently negates that design. The sister contract `MerkleDistributor.sol` implements the same interface without this restriction, confirming the check is erroneous.

### Finding Description

`KernelMerkleDistributor` exposes two public entry points — `claim()` and `claimAndStake()` — both of which delegate to the internal `_processClaim()`:

```solidity
// contracts/KERNEL/KernelMerkleDistributor.sol  lines 311-313
if (account != msg.sender) {
    revert Unauthorized();
}
``` [1](#0-0) 

Both public functions accept an `account` address parameter and forward it to `_processClaim`:

```solidity
function claim(uint256 index, address account, uint256 cumulativeAmount, bytes32[] calldata merkleProof) external
function claimAndStake(uint256 index, address account, uint256 cumulativeAmount, bytes32[] calldata merkleProof) external
``` [2](#0-1) 

The merkle proof already cryptographically binds `index`, `account`, and `cumulativeAmount` together:

```solidity
bytes32 node = keccak256(abi.encodePacked(index, account, cumulativeAmount));
if (!MerkleProofUpgradeable.verify(merkleProof, currentMerkleRoot, node)) {
    revert InvalidMerkleProof();
}
``` [3](#0-2) 

A valid proof can only be constructed for the exact `account` encoded in the merkle tree. There is therefore no security reason to additionally require `msg.sender == account`; the proof itself is the authorization. The reference implementation `MerkleDistributor.sol` — which implements the same `IMerkleDistributor` interface — has no such restriction and allows any caller to submit a proof on behalf of any `account`: [4](#0-3) 

### Impact Explanation

**Impact: Low — Contract fails to deliver promised returns, but doesn't lose value.**

Any address that holds a KERNEL allocation in the merkle tree but cannot directly originate an on-chain transaction is permanently unable to claim:

- Smart-contract wallets (multisigs, DAOs, vaults) that have no built-in `execute` path to call `claim()`.
- Accounts that rely on meta-transaction relayers or ERC-4337 bundlers to submit transactions on their behalf.
- Integrating protocols that batch-claim on behalf of their users.

Tokens remain locked in the distributor indefinitely for such accounts. The tokens are not stolen, but the promised yield/reward is permanently inaccessible to a realistic class of beneficiaries.

### Likelihood Explanation

**Likelihood: Medium.**

Merkle-based reward distributions routinely include smart-contract addresses (protocol treasuries, multisigs, staking vaults). The `account` parameter in the public interface explicitly signals that third-party submission is intended. Any such beneficiary that cannot self-call will trigger the bug without any attacker involvement — it is a passive, always-on failure condition.

### Recommendation

Remove the `account != msg.sender` guard from `_processClaim`. The merkle proof is sufficient authorization:

```diff
-        if (account != msg.sender) {
-            revert Unauthorized();
-        }
-
         if (isClaimed(index, account)) {
``` [1](#0-0) 

### Proof of Concept

1. The protocol allocates KERNEL rewards to `account = 0xMULTISIG` (a Gnosis Safe) in the merkle tree.
2. `0xMULTISIG` has no direct path to call `KernelMerkleDistributor.claim()` (e.g., it is a deprecated safe with lost signers, or a vault contract).
3. A keeper/relayer attempts to call `claim(index, 0xMULTISIG, amount, proof)` from their own EOA.
4. `_processClaim` evaluates `account (0xMULTISIG) != msg.sender (keeper EOA)` → `revert Unauthorized()`.
5. The KERNEL tokens allocated to `0xMULTISIG` remain permanently locked in the distributor. [5](#0-4)

### Citations

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L250-285)
```text
    function claim(
        uint256 index,
        address account,
        uint256 cumulativeAmount,
        bytes32[] calldata merkleProof
    )
        external
        override
        nonReentrant
        whenNotPaused
    {
        uint256 amountToSend = _processClaim(index, account, cumulativeAmount, merkleProof);

        kernel.safeTransfer(account, amountToSend);

        emit Claimed(index, account, amountToSend);
    }

    /// @notice Claims the given amount of the tokens for a given address and automatically stakes them in the
    /// KernelDepositPool contract as part of the same transaction
    function claimAndStake(
        uint256 index,
        address account,
        uint256 cumulativeAmount,
        bytes32[] calldata merkleProof
    )
        external
        nonReentrant
        whenNotPaused
    {
        uint256 amountToStake = _processClaim(index, account, cumulativeAmount, merkleProof);

        IKernelDepositPool(kernelDepositPool).stakeFor(account, amountToStake);

        emit ClaimedAndStaked(index, account, amountToStake);
    }
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L292-313)
```text
    function _processClaim(
        uint256 index,
        address account,
        uint256 cumulativeAmount,
        bytes32[] calldata merkleProof
    )
        internal
        returns (uint256)
    {
        UtilLib.checkNonZeroAddress(account);

        if (currentMerkleRoot == bytes32(0)) {
            revert ZeroValueProvided();
        }

        if (index == 0 || index > currentIndex) {
            revert InvalidIndex();
        }

        if (account != msg.sender) {
            revert Unauthorized();
        }
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L320-323)
```text
        bytes32 node = keccak256(abi.encodePacked(index, account, cumulativeAmount));
        if (!MerkleProofUpgradeable.verify(merkleProof, currentMerkleRoot, node)) {
            revert InvalidMerkleProof();
        }
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L97-147)
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

        emit Claimed(index, account, claimableAmount);
    }
```
