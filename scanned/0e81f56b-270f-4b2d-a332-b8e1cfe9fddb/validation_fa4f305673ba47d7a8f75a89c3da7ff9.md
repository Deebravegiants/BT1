### Title
Smart contract accounts cannot claim KERNEL rewards — permanent yield freeze - (File: contracts/KERNEL/KernelMerkleDistributor.sol)

### Summary
`KernelMerkleDistributor._processClaim` enforces `account == msg.sender`, meaning only an EOA can claim on its own behalf. Any smart contract address included in the merkle distribution tree cannot call `claim()` or `claimAndStake()` and will have its KERNEL tokens permanently frozen.

### Finding Description
`KernelMerkleDistributor._processClaim` contains a hard caller restriction:

```solidity
// contracts/KERNEL/KernelMerkleDistributor.sol L311-313
if (account != msg.sender) {
    revert Unauthorized();
}
```

Both public entry points — `claim()` and `claimAndStake()` — route through this internal function, so neither can be invoked on behalf of a smart contract account. The tokens remain in the distributor contract with no recovery path.

This is a design inconsistency: the sibling contract `MerkleDistributor.sol` (used for other reward distributions in the same repo) has no such restriction and allows any caller to claim for any `account`. [1](#0-0) [2](#0-1) [3](#0-2) 

### Impact Explanation
Any smart contract address (multisig treasury, vault, protocol contract, DAO) included in the KERNEL merkle distribution will be permanently unable to claim its allocated tokens. The tokens remain locked in `KernelMerkleDistributor` with no admin rescue function. This constitutes **permanent freezing of unclaimed yield**.

### Likelihood Explanation
Smart contract addresses are routinely included in reward merkle trees — protocol treasuries, liquidity pools, and multisig wallets are common recipients. The protocol itself uses smart contracts (e.g., `NodeDelegator`, `KernelDepositPool`) that could be reward earners. There is no off-chain filter preventing a smart contract address from appearing in the merkle root.

### Recommendation
Remove the `account != msg.sender` check from `_processClaim` and allow any caller to claim on behalf of `account`, sending tokens directly to `account`. This matches the pattern already used in `MerkleDistributor.sol`:

```solidity
// Remove this block from _processClaim:
if (account != msg.sender) {
    revert Unauthorized();
}
```

Tokens are always sent to `account` (not `msg.sender`), so there is no economic incentive for a third party to grief by claiming on someone else's behalf.

### Proof of Concept
1. Protocol includes a multisig treasury address `0xMULTISIG` in the KERNEL merkle tree with allocation `X`.
2. Any EOA calls `KernelMerkleDistributor.claim(index, 0xMULTISIG, X, proof)`.
3. `_processClaim` reverts at line 311: `0xMULTISIG != msg.sender`.
4. The multisig itself calls `claim(index, 0xMULTISIG, X, proof)` — same revert because the multisig's `call` originates from the multisig contract address, not an EOA.
5. No path exists to claim the tokens; they remain permanently locked in `KernelMerkleDistributor`. [4](#0-3)

### Citations

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L250-266)
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
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L292-346)
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

        if (isClaimed(index, account)) {
            revert AlreadyClaimed();
        }

        // Verify the merkle proof
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

        // Update user claim info
        userClaims[account].lastClaimedIndex = index;
        userClaims[account].cumulativeAmount = cumulativeAmount;

        // Calculate the fee and the amount to send
        uint256 fee = (claimableAmount * feeInBPS) / FEE_DENOMINATOR;
        uint256 amountToSend = claimableAmount - fee;

        if (fee > 0) {
            kernel.safeTransfer(protocolTreasury, fee);
        }

        return amountToSend;
    }
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L96-147)
```text
    /// @inheritdoc IMerkleDistributor
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
