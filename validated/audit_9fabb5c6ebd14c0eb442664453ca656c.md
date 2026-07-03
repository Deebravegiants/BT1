### Title
Inconsistent Deposit Limit Enforcement Between ETH and LST Assets Allows ETH Deposit Cap Bypass - (File: contracts/LRTDepositPool.sol)

### Summary
`LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit` applies the deposit cap check inconsistently: for LST assets it includes the incoming `amount` in the comparison, but for ETH it omits it. Any unprivileged depositor can call `depositETH()` and push total ETH deposits arbitrarily beyond the configured cap in a single transaction.

### Finding Description
The internal function `_checkIfDepositAmountExceedesCurrentLimit` contains a branching check that treats ETH differently from ERC-20 LSTs:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← amount excluded
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← amount included
}
``` [1](#0-0) 

For LSTs the check is `totalAssetDeposits + amount > limit`, which correctly blocks any deposit that would push the total over the cap. For ETH the check is `totalAssetDeposits > limit`, which only blocks deposits when the cap is **already** exceeded. As long as `totalAssetDeposits ≤ limit` at the moment of the call, the ETH branch returns `false` regardless of how large `amount` is, and the deposit proceeds.

This check is invoked by `_beforeDeposit`, which is called by the public `depositETH` entry point: [2](#0-1) [3](#0-2) 

The companion view function `getAssetCurrentLimit` correctly computes the remaining headroom as `limit - totalAssetDeposits` for all assets, so callers querying the limit before depositing will see a non-zero value and expect the deposit to be bounded — but the actual enforcement for ETH is weaker than advertised. [4](#0-3) 

### Impact Explanation
The ETH deposit cap is a risk-management invariant: it bounds the protocol's EigenLayer exposure and limits the blast radius of a slashing or liquidity event. Because the cap is not enforced on the incoming `amount` for ETH, a single depositor can push `totalETHDeposits` from `limit` to `limit + X` in one call, where `X` is unbounded. The protocol mints rsETH for the full over-limit amount, diluting the backing ratio for all existing holders and exposing the protocol to more EigenLayer risk than governance intended.

**Impact: Low** — Contract fails to deliver the promised deposit-limit invariant. No direct fund theft occurs in isolation, but the broken cap can compound with other risk factors (e.g., EigenLayer slashing on the excess ETH).

### Likelihood Explanation
The entry point `depositETH` is permissionless and payable. Any depositor who observes that `totalAssetDeposits` is at or near the ETH cap can send a large ETH value in a single transaction to exceed it. No special role, flash loan, or multi-step setup is required. Likelihood is **High** given the trivial exploit path.

### Recommendation
Include `amount` in the ETH branch of the limit check, mirroring the LST branch:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

This makes the enforcement consistent across all asset types and matches the semantics of `getAssetCurrentLimit`.

### Proof of Concept

1. Admin sets `depositLimitByAsset[ETH_TOKEN] = 1000 ether`.
2. Protocol accumulates `totalAssetDeposits[ETH] = 1000 ether` (exactly at cap).
3. For an LST at this point, `_checkIfDepositAmountExceedesCurrentLimit(lst, 1 ether)` returns `true` → deposit reverts.
4. Attacker calls `depositETH{value: 500 ether}(0, "")`.
5. `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, 500 ether)` evaluates `1000 ether > 1000 ether` → `false` → deposit is **not** blocked.
6. `_mintRsETH` mints rsETH for 500 ETH; `totalAssetDeposits[ETH]` becomes 1500 ether — 50 % over the configured cap.
7. The attacker (or any user) can repeat this in subsequent blocks as long as `totalAssetDeposits` does not exceed the limit at the start of the transaction.

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
