Audit Report

## Title
Unconditional zero-value treasury transfer in `claim()` blocks small-balance claimants when token reverts on zero transfers — (`contracts/utils/MerkleDistributor/MerkleDistributor.sol`)

## Summary
`MerkleDistributor.claim()` unconditionally calls `IERC20(token).safeTransfer(protocolTreasury, fee)` at line 144 even when integer division yields `fee = 0`. When the configured token reverts on zero-value transfers, every claim where `claimableAmount < 10` at `feeInBPS = 1000` will revert, temporarily freezing those users' funds. The sibling contracts `KernelMerkleDistributor.sol` and `KernelTop100MerkleDistributor.sol` both guard this call with `if (fee > 0)`, confirming the omission is an internal code defect.

## Finding Description
In `MerkleDistributor.claim()`, the fee transfer is unconditional:

```solidity
// contracts/utils/MerkleDistributor/MerkleDistributor.sol L138-144
uint256 fee = (claimableAmount * feeInBPS) / 10_000;
uint256 amountToSend = claimableAmount - fee;

IERC20(token).safeTransfer(account, amountToSend);

// Send the fee to the protocol treasury
IERC20(token).safeTransfer(protocolTreasury, fee);  // ← no if (fee > 0) guard
``` [1](#0-0) 

When `feeInBPS = 1000` (the maximum allowed by `MAX_FEE_IN_BPS`) and `claimableAmount ∈ [1, 9]`, Solidity integer division truncates `fee` to `0`. The unconditional `safeTransfer(protocolTreasury, 0)` then reverts on any ERC20 that disallows zero-value transfers. Because the transaction is atomic, the state updates at lines 134–135 are also rolled back, leaving the user permanently unable to claim until the fee is reduced or their cumulative amount grows.

The existing `claimableAmount == 0` guard at line 129 only prevents zero claimable amounts; it does not protect against a zero-valued fee derived from a non-zero claimable amount. [2](#0-1) 

Both sibling contracts in the same codebase explicitly guard this path:

```solidity
// KernelMerkleDistributor.sol L341-343
if (fee > 0) {
    kernel.safeTransfer(protocolTreasury, fee);
}
``` [3](#0-2) 

```solidity
// KernelTop100MerkleDistributor.sol L332-334
if (fee > 0) {
    kernel.safeTransfer(protocolTreasury, fee);
}
``` [4](#0-3) 

The `MerkleDistributor` is generic: `setToken` allows the owner to configure any ERC20, and `setFeeInBPS` allows any value up to `MAX_FEE_IN_BPS = 1000`. [5](#0-4) [6](#0-5) 

## Impact Explanation
Users whose incremental `claimableAmount` falls in `[1, 9]` at `feeInBPS = 1000` cannot execute `claim()`. Their funds are locked in the contract until either the owner reduces `feeInBPS` or the user's cumulative claimable amount grows to ≥ 10. This is a concrete, reproducible **temporary freezing of funds**, matching the allowed Medium impact.

## Likelihood Explanation
- `feeInBPS = 1000` is a valid, explicitly bounded owner-settable value; no misconfiguration is required.
- The contract is generic (`setToken` accepts any ERC20); multiple deployed tokens (e.g., LEND, BNB) are known to revert on zero-value transfers.
- No attacker action is required — the condition arises from normal protocol configuration combined with small claimable balances.
- Any unprivileged user calling `claim()` with a qualifying leaf can trigger the revert.

## Recommendation
Add the same `if (fee > 0)` guard used in the sibling contracts:

```solidity
if (fee > 0) {
    IERC20(token).safeTransfer(protocolTreasury, fee);
}
```

## Proof of Concept
1. Deploy an ERC20 token that reverts on `transfer(to, 0)`.
2. Deploy `MerkleDistributor`, initialize with `feeInBPS = 1000` and the token above.
3. Build a merkle tree with a leaf `(index=1, user=Alice, cumulativeAmount=5)` and set the root.
4. Call `claim(1, Alice, 5, proof)`.
5. Observe revert at `safeTransfer(protocolTreasury, 0)` — `fee = (5 * 1000) / 10000 = 0`.
6. Call `setFeeInBPS(0)` as owner, then repeat step 4 — `claim()` succeeds.
7. Alternatively, use `cumulativeAmount = 10` — `fee = 1 > 0`, `claim()` succeeds without the owner change.

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L47-47)
```text
    uint256 public constant MAX_FEE_IN_BPS = 1000;
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L129-131)
```text
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

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L185-192)
```text
    function setToken(address _token) external onlyOwner {
        if (_token == address(0)) {
            revert ZeroValueProvided();
        }

        token = _token;

        emit TokenUpdated(_token);
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L341-343)
```text
        if (fee > 0) {
            kernel.safeTransfer(protocolTreasury, fee);
        }
```

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L332-334)
```text
        if (fee > 0) {
            kernel.safeTransfer(protocolTreasury, fee);
        }
```
