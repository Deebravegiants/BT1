Looking at the vulnerability class from the external report — a state-transition check that is incomplete, allowing extra commitments/deposits after a limit is reached — I need to find the analog in LRT-rsETH. Let me examine the deposit limit enforcement in `LRTDepositPool`.

### Title
ETH Deposit Limit Check Ignores Incoming Deposit Amount, Allowing Unlimited Over-Deposit Beyond Protocol Cap - (File: contracts/LRTDepositPool.sol)

---

### Summary

`LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit` applies a fundamentally different — and broken — guard for ETH versus ERC20 tokens. For ETH, the incoming `amount` is silently discarded; the function only tests whether the *current* total already exceeds the cap. Any depositor can therefore push ETH holdings arbitrarily above the configured limit in a single transaction, causing unbounded rsETH over-minting and diluting every existing holder.

---

### Finding Description

`_checkIfDepositAmountExceedesCurrentLimit` (lines 676–682) contains an asymmetric branch:

```solidity
// contracts/LRTDepositPool.sol  L676-L682
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)); // ← amount ignored
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← correct for ERC20
}
```

For ERC20 assets the prospective deposit is added before comparing against the cap, so a deposit that *would* breach the limit is correctly rejected. For ETH the `amount` parameter is never used; the guard only fires when the cap is **already** exceeded. Consequently, whenever `totalAssetDeposits <= depositLimit`, `depositETH` accepts any `msg.value` without restriction.

This is the direct structural analog of the Crowdsale bug: `_addCommitment` checked only `block.timestamp` and ignored `auctionEnded()` / `status.finalized`, allowing commitments after the auction was effectively closed. Here, `_checkIfDepositAmountExceedesCurrentLimit` checks only the pre-deposit total and ignores the incoming amount, allowing deposits that blow past the cap.

The call path is fully public and unprivileged:

```
depositETH(minRSETHAmountExpected, referralId)   [payable, nonReentrant, whenNotPaused]
  └─ _beforeDeposit(ETH_TOKEN, msg.value, ...)
       └─ _checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, msg.value)
            └─ returns false when totalAssetDeposits <= depositLimit  ← bug
  └─ _mintRsETH(rsethAmountToMint)               ← rsETH minted for full msg.value
``` [1](#0-0) [2](#0-1) [3](#0-2) 

---

### Impact Explanation

**Protocol insolvency / Critical.**

The deposit limit exists to cap the protocol's EigenLayer exposure. When it is bypassed:

1. `_mintRsETH` mints rsETH proportional to the full `msg.value` at the current oracle rate. [4](#0-3) 
2. `getTotalAssetDeposits` — which aggregates ETH across the deposit pool, all NDCs, EigenLayer strategies, the converter, and the unstaking vault — will now exceed `depositLimitByAsset(ETH)` by the full over-deposit. [5](#0-4) 
3. `getAssetCurrentLimit` returns 0 only *after* the fact; it cannot undo the already-minted rsETH. [6](#0-5) 
4. The rsETH supply is now inflated beyond what the protocol's risk parameters were designed to support. If EigenLayer suffers a slashing event at the over-exposed scale, the protocol cannot make all rsETH holders whole — the last withdrawers face a shortfall, mirroring the Crowdsale fund-freeze outcome.

---

### Likelihood Explanation

**High.** The entry point is `depositETH`, which is public, payable, and requires no special role. An attacker needs only to observe that `totalAssetDeposits <= depositLimit` (trivially readable on-chain via `getTotalAssetDeposits`) and send a single large ETH deposit. No front-running, governance capture, or oracle manipulation is required. The condition `totalAssetDeposits <= depositLimit` is the normal operating state of the protocol for most of its lifetime.

---

### Recommendation

Apply the same prospective check used for ERC20 tokens:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    // Unified check: include the incoming amount for both ETH and ERC20
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
``` [1](#0-0) 

---

### Proof of Concept

```
depositLimit  = 1 000 ETH
totalAssetDeposits (before) = 999 ETH

Attacker calls depositETH{value: 5000 ETH}(0, "")

_checkIfDepositAmountExceedesCurrentLimit(ETH, 5000 ETH):
  totalAssetDeposits = 999 ETH
  branch: ETH → return (999 > 1000) = false   ← NOT blocked

_mintRsETH mints rsETH for 5000 ETH at current rate.

totalAssetDeposits (after) = 5 999 ETH  (≈ 6× the intended cap)
```

The next depositor is correctly blocked (`5999 > 1000 = true`), but the damage — 5 000 ETH of unbacked-beyond-limit rsETH already minted — is irreversible without a governance intervention. Existing rsETH holders are diluted and the protocol's EigenLayer exposure is 6× the intended maximum, creating insolvency risk under any slashing scenario.

### Citations

**File:** contracts/LRTDepositPool.sol (L76-93)
```text
    function depositETH(
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        payable
        nonReentrant
        whenNotPaused
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L385-397)
```text
    function getTotalAssetDeposits(address asset) public view override returns (uint256 totalAssetDeposit) {
        (
            uint256 assetLyingInDepositPool,
            uint256 assetLyingInNDCs,
            uint256 assetStakedInEigenLayer,
            uint256 assetUnstakingFromEigenLayer,
            uint256 assetLyingInConverter,
            uint256 assetLyingUnstakingVault
        ) = getAssetDistributionData(asset);
        uint256 effectiveAssetWithEigenLayer = assetStakedInEigenLayer + assetUnstakingFromEigenLayer;
        return (assetLyingInDepositPool + assetLyingInNDCs + effectiveAssetWithEigenLayer + assetLyingInConverter
                + assetLyingUnstakingVault);
    }
```

**File:** contracts/LRTDepositPool.sol (L402-409)
```text
    function getAssetCurrentLimit(address asset) public view override returns (uint256) {
        uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
        if (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)) {
            return 0;
        }

        return lrtConfig.depositLimitByAsset(asset) - totalAssetDeposits;
    }
```

**File:** contracts/LRTDepositPool.sol (L648-670)
```text
    function _beforeDeposit(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected
    )
        private
        view
        returns (uint256 rsethAmountToMint)
    {
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
    }
```

**File:** contracts/LRTDepositPool.sol (L676-682)
```text
    function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
        uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
        if (asset == LRTConstants.ETH_TOKEN) {
            return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
        }
        return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
    }
```

**File:** contracts/LRTDepositPool.sol (L686-690)
```text
    function _mintRsETH(uint256 rsethAmountToMint) private {
        address rsethToken = lrtConfig.rsETH();
        // mint rseth for user
        IRSETH(rsethToken).mint(msg.sender, rsethAmountToMint);
    }
```
