### Title
Dust Token Donation Permanently Blocks `removeNodeDelegatorContractFromQueue` — (File: `contracts/LRTDepositPool.sol`)

### Summary
An unprivileged attacker can permanently prevent the admin from removing any NodeDelegator from the queue by donating 1 wei of any supported LST (or 1 wei of ETH) directly to the NodeDelegator contract. The residue-balance guards `_checkResidueLSTBalance` and `_checkResidueEthBalance` compare the NodeDelegator's live `balanceOf` against `maxNegligibleAmount`, which is **zero by default** (never set in `initialize`). Any non-zero balance causes an unconditional revert, making `removeNodeDelegatorContractFromQueue` permanently unusable for that NDC until the admin separately calls `setMaxNegligibleAmount`.

---

### Finding Description

`removeNodeDelegatorContractFromQueue` calls two internal guards before removing an NDC:

**`_checkResidueEthBalance`** — reverts if the NDC's raw ETH balance exceeds `maxNegligibleAmount`:

```solidity
// LRTDepositPool.sol lines 616-624
function _checkResidueEthBalance(address nodeDelegatorAddress) internal view {
    if (
        INodeDelegator(nodeDelegatorAddress).getEffectivePodShares() != 0
            || address(nodeDelegatorAddress).balance > maxNegligibleAmount   // ← griefable
            || INodeDelegator(nodeDelegatorAddress).getAssetUnstaking(LRTConstants.ETH_TOKEN) > 0
    ) {
        revert NodeDelegatorHasETH();
    }
}
```

**`_checkResidueLSTBalance`** — reverts if the NDC's ERC-20 balance of any supported asset exceeds `maxNegligibleAmount`:

```solidity
// LRTDepositPool.sol lines 627-646
assetBalance = IERC20(supportedAssets[i]).balanceOf(nodeDelegatorAddress)
    + INodeDelegator(nodeDelegatorAddress).getAssetBalance(supportedAssets[i]);
assetBalance += INodeDelegator(nodeDelegatorAddress).getAssetUnstaking(supportedAssets[i]);

if (assetBalance > maxNegligibleAmount) {          // ← griefable when maxNegligibleAmount == 0
    revert NodeDelegatorHasAssetBalance(supportedAssets[i], assetBalance);
}
```

`maxNegligibleAmount` is declared as a plain storage variable with **no initialisation** in `initialize`:

```solidity
// LRTDepositPool.sol line 36
uint256 public maxNegligibleAmount;   // defaults to 0
```

The NodeDelegator accepts arbitrary ETH via its open `receive()`:

```solidity
// NodeDelegator.sol line 81-83
receive() external payable {
    emit ETHReceived(msg.sender, msg.value);
}
```

Because both guards compare against `maxNegligibleAmount == 0`, a donation of **1 wei** of ETH or 1 wei of any supported LST to the NDC is sufficient to make every future call to `removeNodeDelegatorContractFromQueue` revert for that NDC.

---

### Impact Explanation

The admin loses the ability to remove a targeted NodeDelegator from the queue. While no user funds are directly stolen, the protocol's operational guarantee — that an admin can decommission an NDC — is broken. If the NDC must be removed urgently (e.g., operator key compromise, strategy deprecation), the attacker can continuously re-donate dust to block every removal attempt. The admin must first call `setMaxNegligibleAmount` with a value exceeding the attacker's donation, adding an out-of-band remediation step that is not documented or expected.

**Impact class:** Low — contract fails to deliver promised returns (NDC removal), but no funds are lost.

---

### Likelihood Explanation

The attack costs only gas plus 1 wei of any supported LST or ETH. It requires no special privilege. The attacker can repeat the donation after every admin `setMaxNegligibleAmount` call, creating a persistent cat-and-mouse dynamic. Any user who holds even a dust amount of stETH, ETHx, or another supported LST can execute this.

---

### Recommendation

Initialise `maxNegligibleAmount` to a sensible non-zero dust threshold (e.g., `1e6` wei) inside `initialize`, so that the guards are not trivially bypassable from deployment:

```solidity
function initialize(address lrtConfigAddr) external initializer {
    ...
    maxNegligibleAmount = 1e6;   // dust threshold; admin can adjust later
    ...
}
```

Alternatively, replace the live-balance check with a snapshot-based approach (record the balance at the time the NDC is flagged for removal) so that post-flag donations cannot affect the outcome.

---

### Proof of Concept

1. Admin decides to remove `nodeDelegatorAddress` and calls `removeNodeDelegatorContractFromQueue(nodeDelegatorAddress)`.
2. Attacker (any address) calls `stETH.transfer(nodeDelegatorAddress, 1)` — costs ~1 wei + gas.
3. Inside `_checkResidueLSTBalance`, `IERC20(stETH).balanceOf(nodeDelegatorAddress)` returns `1`.
4. `1 > 0 (maxNegligibleAmount)` → `revert NodeDelegatorHasAssetBalance(stETH, 1)`.
5. Admin's removal transaction reverts. The NDC remains in the queue indefinitely.
6. Admin calls `setMaxNegligibleAmount(2)`. Attacker immediately calls `stETH.transfer(nodeDelegatorAddress, 3)`. Step 4 repeats. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/LRTDepositPool.sol (L36-36)
```text
    uint256 public maxNegligibleAmount;
```

**File:** contracts/LRTDepositPool.sol (L274-277)
```text
    function setMaxNegligibleAmount(uint256 maxNegligibleAmount_) external onlyLRTAdmin {
        maxNegligibleAmount = maxNegligibleAmount_;
        emit MaxNegligibleAmountUpdated(maxNegligibleAmount_);
    }
```

**File:** contracts/LRTDepositPool.sol (L616-624)
```text
    function _checkResidueEthBalance(address nodeDelegatorAddress) internal view {
        if (
            INodeDelegator(nodeDelegatorAddress).getEffectivePodShares() != 0
                || address(nodeDelegatorAddress).balance > maxNegligibleAmount
                || INodeDelegator(nodeDelegatorAddress).getAssetUnstaking(LRTConstants.ETH_TOKEN) > 0
        ) {
            revert NodeDelegatorHasETH();
        }
    }
```

**File:** contracts/LRTDepositPool.sol (L627-646)
```text
    function _checkResidueLSTBalance(address nodeDelegatorAddress) internal view {
        address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
        uint256 supportedAssetsLength = supportedAssets.length;

        uint256 assetBalance;
        for (uint256 i; i < supportedAssetsLength; ++i) {
            if (supportedAssets[i] == LRTConstants.ETH_TOKEN) {
                // this function only checks for residual LST balance
                continue;
            }

            assetBalance = IERC20(supportedAssets[i]).balanceOf(nodeDelegatorAddress)
                + INodeDelegator(nodeDelegatorAddress).getAssetBalance(supportedAssets[i]);
            assetBalance += INodeDelegator(nodeDelegatorAddress).getAssetUnstaking(supportedAssets[i]);

            if (assetBalance > maxNegligibleAmount) {
                revert NodeDelegatorHasAssetBalance(supportedAssets[i], assetBalance);
            }
        }
    }
```

**File:** contracts/NodeDelegator.sol (L81-83)
```text
    receive() external payable {
        emit ETHReceived(msg.sender, msg.value);
    }
```
