The full contract is visible. Let me analyze the `claim` function precisely.

**Key observations from `MerkleBlastPointsDistributor.claim()` (lines 86–131):**

1. **No `msg.sender == account` guard.** The function accepts an arbitrary `account` parameter and never checks that `msg.sender == account`. [1](#0-0) 

2. **Any caller can trigger state updates for any account.** After proof verification, `userClaims[account].lastClaimedIndex`, `cumulativeBlastPointAmount`, and `cumulativeBlastGoldAmount` are written for the victim, and `Claimed` is emitted — all without the victim's involvement. [2](#0-1) 

3. **No actual Blast Points transfer occurs on-chain.** The `claim()` function never calls the `blastPointAddress` contract to deliver points. The contract only configures a points operator at initialization; actual point delivery is off-chain or operator-driven. [3](#0-2) 

4. **`isClaimed` permanently blocks re-claim.** Once an attacker sets `lastClaimedIndex >= index` for the victim, the victim's subsequent `claim()` call reverts with `AlreadyClaimed`. [4](#0-3) 

5. **Contrast with `KernelMerkleDistributor`.** The sibling contract explicitly guards against this with `if (account != msg.sender) revert Unauthorized();`. `MerkleBlastPointsDistributor` has no equivalent check. [5](#0-4) 

The vulnerability is real and concrete. Here is the full finding:

---

### Title
Unprivileged caller can grief victim's Blast Points claim by front-running `claim()` without `msg.sender == account` guard — (`contracts/utils/MerkleDistributor/MerkleBlastPointsDistributor.sol`)

### Summary
`MerkleBlastPointsDistributor.claim()` accepts an arbitrary `account` address and performs no check that `msg.sender == account`. Any third party can call `claim()` with a victim's valid merkle proof, permanently marking the victim's on-chain state as claimed while the actual Blast Points are never delivered to the victim.

### Finding Description
The `claim()` function verifies a merkle proof tied to `(index, account, cumulativeBlastPointAmount, cumulativeBlastGoldAmount)` and then writes to `userClaims[account]` and emits `Claimed`. Because merkle proofs are public (derivable from the merkle tree), any attacker can supply a victim's valid proof and invoke `claim()` on their behalf.

The contract itself never calls the Blast Points protocol to transfer points — it only configures a points operator at initialization. Actual point delivery is therefore off-chain or operator-driven, and the off-chain system is expected to observe the `Claimed` event or the on-chain state to determine who has claimed. If the off-chain delivery system requires `msg.sender == account` (i.e., the account holder must be the transaction sender), the attacker's call satisfies the on-chain state machine but not the off-chain delivery condition, leaving the victim with no points and no ability to re-claim.

Even if the off-chain system does not gate on `msg.sender`, the victim's `lastClaimedIndex` is permanently advanced, preventing any future claim for that index via `AlreadyClaimed`.

### Impact Explanation
- The victim's on-chain claim state is permanently consumed.
- The victim cannot re-claim for the same index.
- If the off-chain Blast Points delivery system requires the account holder to be `msg.sender`, the victim receives zero points despite the `Claimed` event being emitted.
- No funds are stolen; the contract fails to deliver its promised returns.
- **Impact: Low — Contract fails to deliver promised returns, but doesn't lose value.**

### Likelihood Explanation
- Merkle proofs are public data; any observer of the merkle tree can construct a valid proof for any account.
- No special role, key, or privilege is required.
- The attacker only needs to call a public, unpaused function.
- **Likelihood: Medium** (requires the attacker to act before the victim, but is trivially executable by anyone monitoring the mempool or the merkle tree).

### Recommendation
Add a `msg.sender == account` check at the top of `claim()`, mirroring the guard already present in `KernelMerkleDistributor._processClaim()`:

```solidity
if (account != msg.sender) {
    revert Unauthorized();
}
```

This ensures only the account holder can trigger their own claim, preventing third-party grief.

### Proof of Concept

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.27;

// Fork or local test — no public mainnet testing
contract MerkleBlastPointsDistributorGriefTest is Test {
    MerkleBlastPointsDistributor distributor;
    address victim  = address(0xBEEF);
    address attacker = address(0xBAD);

    function setUp() public {
        // Deploy and initialize distributor (mock blastPointAddress)
        distributor = new MerkleBlastPointsDistributor();
        distributor.initialize(address(mockBlast), address(operator));

        // Build a single-leaf merkle tree for victim
        // leaf = keccak256(abi.encodePacked(1, victim, 1000e18, 500e18))
        bytes32 leaf = keccak256(abi.encodePacked(uint256(1), victim, uint256(1000e18), uint256(500e18)));
        distributor.setMerkleRoot(leaf); // single-leaf tree: root == leaf, proof == []
    }

    function testAttackerGriefsVictim() public {
        bytes32[] memory proof = new bytes32[](0);

        // Attacker calls claim on behalf of victim
        vm.prank(attacker);
        distributor.claim(1, victim, 1000e18, 500e18, proof);

        // Victim's state is now marked claimed
        assertEq(distributor.userClaims(victim).lastClaimedIndex, 1);

        // Victim cannot claim their own points
        vm.prank(victim);
        vm.expectRevert(IMerkleBlastPointsDistributor.AlreadyClaimed.selector);
        distributor.claim(1, victim, 1000e18, 500e18, proof);

        // msg.sender was attacker throughout — victim never received points
    }
}
```

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleBlastPointsDistributor.sol (L70-76)
```text
    function initialize(address _blastPointAddress, address _pointsOperator) external initializer {
        __Ownable_init();
        __Pausable_init();

        blastPointAddress = _blastPointAddress;
        IBlastPoints(blastPointAddress).configurePointsOperator(_pointsOperator);
    }
```

**File:** contracts/utils/MerkleDistributor/MerkleBlastPointsDistributor.sol (L79-83)
```text
    function isClaimed(uint256 index, address account) public view override returns (bool) {
        if (index == 0) revert ZeroValueProvided();

        return userClaims[account].lastClaimedIndex >= index;
    }
```

**File:** contracts/utils/MerkleDistributor/MerkleBlastPointsDistributor.sol (L86-96)
```text
    function claim(
        uint256 index,
        address account,
        uint256 cumulativeBlastPointAmount,
        uint256 cumulativeBlastGoldAmount,
        bytes32[] calldata merkleProof
    )
        external
        override
        whenNotPaused
    {
```

**File:** contracts/utils/MerkleDistributor/MerkleBlastPointsDistributor.sol (L125-130)
```text
        // Update user claim info
        userClaims[account].lastClaimedIndex = index;
        userClaims[account].cumulativeBlastPointAmount = cumulativeBlastPointAmount;
        userClaims[account].cumulativeBlastGoldAmount = cumulativeBlastGoldAmount;

        emit Claimed(index, account, claimableBlastPoints, claimableBlastGold);
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L311-313)
```text
        if (account != msg.sender) {
            revert Unauthorized();
        }
```
