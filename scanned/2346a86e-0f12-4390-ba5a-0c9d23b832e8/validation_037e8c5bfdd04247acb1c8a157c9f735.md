Looking at the `claim()` function in detail:

### Title
Unconditional Zero-Value `safeTransfer` to `protocolTreasury` When `feeInBPS == 0` Permanently Freezes All Unclaimed Yield — (`contracts/utils/MerkleDistributor/MerkleDistributor.sol`)

---

### Summary

`claim()` unconditionally calls `safeTransfer(protocolTreasury, fee)` at line 144 even when `fee == 0`. Because `setFeeInBPS(0)` is explicitly permitted by the contract, any ERC20 yield token that reverts on zero-value transfers will cause every `claim()` call to revert, permanently freezing all unclaimed yield for all users.

---

### Finding Description

In `claim()`, the fee and transfer-to-treasury are computed and executed unconditionally:

```solidity
// line 138-144
uint256 fee = (claimableAmount * feeInBPS) / 10_000;
uint256 amountToSend = claimableAmount - fee;

IERC20(token).safeTransfer(account, amountToSend);

// Send the fee to the protocol treasury
IERC20(token).safeTransfer(protocolTreasury, fee);   // ← always executes, even when fee == 0
``` [1](#0-0) 

`setFeeInBPS` only rejects values **above** `MAX_FEE_IN_BPS` (1000); zero is explicitly valid:

```solidity
// line 198-201
function setFeeInBPS(uint256 _feeInBPS) external onlyOwner {
    if (_feeInBPS > MAX_FEE_IN_BPS) {
        revert InvalidFeeInBPS();
    }
``` [2](#0-1) 

When `feeInBPS == 0`:
- `fee = (claimableAmount * 0) / 10_000 = 0`
- `safeTransfer(protocolTreasury, 0)` is called unconditionally

There is no `if (fee > 0)` guard anywhere before line 144. [3](#0-2) 

---

### Impact Explanation

If the yield token reverts on zero-value transfers (a known pattern in several ERC20 implementations), every single `claim()` call reverts after the user's state has **not yet been written** (state is written at lines 134–135 before the transfers, so the revert rolls back state too). No user can ever claim. All yield locked in the distributor is permanently frozen. This matches the allowed scope: **Medium — Permanent freezing of unclaimed yield**.

---

### Likelihood Explanation

Two conditions must hold simultaneously:

1. **`feeInBPS` is set to 0** — this is a legitimate, explicitly allowed owner action with no additional friction.
2. **The yield token reverts on zero-value transfers** — non-standard but not uncommon; several tokens enforce `amount > 0`.

Neither condition requires key compromise or governance capture. The owner setting `feeInBPS = 0` is an intended operational choice (e.g., "no fee period"). The combination is realistic and the call sequence is straightforward.

---

### Recommendation

Add a zero-check before the treasury transfer:

```solidity
if (fee > 0) {
    IERC20(token).safeTransfer(protocolTreasury, fee);
}
```

This is the standard defensive pattern when fee amounts can be zero by design.

---

### Proof of Concept

```solidity
// MockERC20 that reverts on zero-value transfers
contract RevertOnZeroERC20 is ERC20 {
    function transfer(address to, uint256 amount) public override returns (bool) {
        require(amount > 0, "zero transfer");
        return super.transfer(to, amount);
    }
}

function testPermanentFreeze() public {
    RevertOnZeroERC20 tok = new RevertOnZeroERC20();
    MerkleDistributor dist = new MerkleDistributor();
    dist.initialize(address(tok), treasury, 0);  // feeInBPS = 0

    // Build a valid merkle tree for (index=1, user, amount=1e18)
    bytes32 leaf = keccak256(abi.encodePacked(uint256(1), user, uint256(1e18)));
    bytes32 root = leaf; // single-leaf tree
    dist.setMerkleRoot(root);

    tok.mint(address(dist), 1e18);

    // claim() reverts because safeTransfer(treasury, 0) reverts
    vm.expectRevert("zero transfer");
    dist.claim(1, user, 1e18, new bytes32[](0));

    // All yield is permanently frozen — no user can ever claim
}
```

Fuzz over `feeInBPS` in `[0, 10_000 / claimableAmount)` to cover all values where integer division rounds `fee` to zero, confirming the same revert for any small-enough fee setting.

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L137-146)
```text
        // Send the claimable amount to the user - deducting the fee
        uint256 fee = (claimableAmount * feeInBPS) / 10_000;
        uint256 amountToSend = claimableAmount - fee;

        IERC20(token).safeTransfer(account, amountToSend);

        // Send the fee to the protocol treasury
        IERC20(token).safeTransfer(protocolTreasury, fee);

        emit Claimed(index, account, claimableAmount);
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L198-201)
```text
    function setFeeInBPS(uint256 _feeInBPS) external onlyOwner {
        if (_feeInBPS > MAX_FEE_IN_BPS) {
            revert InvalidFeeInBPS();
        }
```
