### Title
Missing Minimum-Shares Guard Enables Block-Stuffing to Silently Reduce KING Shares Received — (`contracts/king-protocol/TokenSwap.sol`)

---

### Summary

`depositToKingProtocol` sets its return value to the result of `previewDeposit` and then calls `kingProtocol.deposit`, but `deposit` returns `void` so actual minted shares are never captured. There is no `minShares` parameter or post-deposit balance check to revert if actual shares fall below expectation. An attacker can stuff blocks to delay the manager's transaction until King Protocol's rate or fee schedule changes, causing the protocol to silently receive fewer KING shares than the manager anticipated.

---

### Finding Description

In `depositToKingProtocol`:

```solidity
(uint256 expectedShares,) = kingProtocol.previewDeposit(tokens, amounts);
shareReceived = expectedShares;                          // ← set to preview, not actual

assetToken.forceApprove(address(kingProtocol), amount);
kingProtocol.deposit(tokens, amounts, address(this));   // ← returns void; actual shares never read
assetToken.forceApprove(address(kingProtocol), 0);

emit TokensDeposited(asset, amount, shareReceived, msg.sender);
``` [1](#0-0) 

`IKingProtocol.deposit` is declared `external` with no return value:

```solidity
function deposit(address[] memory _tokens, uint256[] memory _amounts, address _receiver) external;
``` [2](#0-1) 

Because `deposit` is void, the contract has no way to compare actual minted shares against the preview. `shareReceived` is always the preview estimate, and no guard reverts the transaction if the actual KING balance increase is lower.

The same structural flaw exists in `depositMultipleToKingProtocol`: [3](#0-2) 

---

### Impact Explanation

**Low — Block stuffing / contract fails to deliver promised returns.**

If King Protocol has a time-varying fee or rate (e.g., a deposit fee that steps up at certain blocks or a TVL-based rate), an attacker can fill every block with high-gas transactions until the rate changes unfavorably. When the manager's transaction finally lands, `previewDeposit` and `deposit` both execute at the new (worse) rate in the same transaction. The protocol receives fewer KING shares than the manager expected when they signed the transaction, with no revert and no on-chain record of the shortfall (the emitted `shareReceived` is the preview value, not the actual balance delta).

---

### Likelihood Explanation

- Block stuffing requires significant ETH to sustain across multiple blocks, making it expensive.
- The attacker gains nothing directly; the impact is protocol-side loss of yield/shares.
- However, the missing slippage guard is a latent defect that can also be triggered by ordinary network congestion or any King Protocol rate update, without any attacker involvement.
- The `onlyAdminOrManager` gate limits the entry point but does not mitigate the missing guard.

---

### Recommendation

1. **Add a `minShares` parameter** to `depositToKingProtocol` and `depositMultipleToKingProtocol` and revert if actual shares received fall below it.
2. **Capture actual shares via balance delta** rather than trusting `previewDeposit`, since `IKingProtocol.deposit` returns void:

```solidity
uint256 kingBefore = kingToken.balanceOf(address(this));
kingProtocol.deposit(tokens, amounts, address(this));
uint256 actualShares = kingToken.balanceOf(address(this)) - kingBefore;
require(actualShares >= minShares, "Slippage: insufficient shares");
shareReceived = actualShares;
```

---

### Proof of Concept

Deploy a mock `IKingProtocol` where:
- `previewDeposit` returns `X` shares at block `N`
- `deposit` mints `X - delta` shares at block `N+k` (simulating a fee increase)

Call `depositToKingProtocol` after advancing `k` blocks (fork-test with `vm.roll`). Assert:
- No revert occurs
- `shareReceived` == `X - delta` (preview at new rate), but the actual KING balance increase is also `X - delta` — confirming the protocol silently accepted fewer shares than the manager's off-chain decision assumed, with no slippage protection and no revert path.

### Citations

**File:** contracts/king-protocol/TokenSwap.sol (L177-189)
```text
        (uint256 expectedShares,) = kingProtocol.previewDeposit(tokens, amounts);
        shareReceived = expectedShares;

        // Approve King Protocol to spend the tokens
        assetToken.forceApprove(address(kingProtocol), amount);

        // Deposit to King Protocol
        kingProtocol.deposit(tokens, amounts, address(this));

        // Reset approval after successful deposit
        assetToken.forceApprove(address(kingProtocol), 0);

        emit TokensDeposited(asset, amount, shareReceived, msg.sender);
```

**File:** contracts/king-protocol/TokenSwap.sol (L210-214)
```text
        (uint256 expectedShares,) = kingProtocol.previewDeposit(assets, amounts);
        shareReceived = expectedShares;

        _approveTokensForDeposit(assets, amounts);
        kingProtocol.deposit(assets, amounts, address(this));
```

**File:** contracts/king-protocol/IKingProtocol.sol (L11-11)
```text
    function deposit(address[] memory _tokens, uint256[] memory _amounts, address _receiver) external;
```
