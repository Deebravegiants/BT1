### Title
Attacker Can Block All New LST Deposits by Directly Transferring Tokens to LRTDepositPool - (File: contracts/LRTDepositPool.sol)

### Summary
`LRTDepositPool.getAssetDistributionData()` measures the pool's LST balance via a raw `balanceOf(address(this))` call. Because the contract accepts direct token transfers, any unprivileged actor can inflate this balance without going through `depositAsset()`, pushing `getTotalAssetDeposits()` above `depositLimitByAsset` and causing every subsequent `depositAsset()` call to revert with `MaximumDepositLimitReached`.

### Finding Description
`getAssetDistributionData()` computes the pool's share of a supported asset as:

```solidity
assetLyingInDepositPool = IERC20(asset).balanceOf(address(this));
``` [1](#0-0) 

This raw balance feeds directly into `getTotalAssetDeposits()`:

```solidity
return (assetLyingInDepositPool + assetLyingInNDCs + effectiveAssetWithEigenLayer
        + assetLyingInConverter + assetLyingUnstakingVault);
``` [2](#0-1) 

`getTotalAssetDeposits()` is then consumed by `_checkIfDepositAmountExceedesCurrentLimit()`, which gates every deposit:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    ...
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
``` [3](#0-2) 

When this check returns `true`, `_beforeDeposit()` reverts:

```solidity
if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
    revert MaximumDepositLimitReached();
}
``` [4](#0-3) 

`LRTDepositPool` has no mechanism to reject direct ERC-20 transfers. An attacker who holds any amount of a supported LST (stETH, ETHx, etc.) can call `IERC20(asset).transfer(address(lrtDepositPool), amount)` directly, bypassing all deposit-limit accounting. The inflated `balanceOf` is immediately reflected in `assetLyingInDepositPool`, making `getTotalAssetDeposits` exceed `depositLimitByAsset` and freezing all new deposits.

The same inflated value also propagates into `LRTOracle._getTotalEthInProtocol()` via `ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset)`, which is called inside the public `updateRSETHPrice()`:

```solidity
uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
totalETHInProtocol += totalAssetAmt.mulWad(assetER);
``` [5](#0-4) 

This artificially inflates the reported TVL, which in turn inflates `newRsETHPrice`, potentially triggering the `PriceAboveDailyThreshold` revert for non-manager callers and blocking price updates as well.

### Impact Explanation
**Medium — Temporary freezing of funds.**

All new deposits of the targeted LST are blocked until an admin raises `depositLimitByAsset`. The attacker's tokens are permanently donated to the protocol (they become part of the TVL), but the attacker can repeat the attack cheaply whenever the admin raises the limit. Users cannot deposit, and the protocol's deposit functionality is effectively frozen for the targeted asset.

### Likelihood Explanation
**Medium.**

Any holder of a supported LST (stETH, ETHx) can execute this attack. The cost scales with how far the current `totalAssetDeposits` is below `depositLimitByAsset`. When the protocol is operating near its deposit cap — a common operational state — even a dust-level transfer suffices. The attacker permanently loses the transferred tokens, but the griefing cost is low relative to the disruption caused.

### Recommendation
Replace the raw `balanceOf` accounting with an internal deposit ledger. Track only tokens received through the official `depositAsset()` / `depositETH()` entry points:

```solidity
mapping(address asset => uint256 amount) internal _trackedDeposits;

// In depositAsset():
_trackedDeposits[asset] += depositAmount;

// In getAssetDistributionData():
assetLyingInDepositPool = _trackedDeposits[asset];
```

Alternatively, add a `sweep` function that allows the admin to recover unaccounted tokens (tokens whose balance exceeds `_trackedDeposits`) so the deposit limit is not artificially inflated.

### Proof of Concept

1. Protocol state: `depositLimitByAsset[stETH] = 100_000 ether`, current `getTotalAssetDeposits(stETH) = 99_990 ether`.
2. Attacker calls `stETH.transfer(address(lrtDepositPool), 20 ether)` directly — no `depositAsset()` call, no limit check.
3. `getAssetDistributionData(stETH)` now returns `assetLyingInDepositPool = 99_990 + 20 = 100_010 ether` (raw `balanceOf`).
4. `getTotalAssetDeposits(stETH)` returns `100_010 ether`.
5. Any user calling `depositAsset(stETH, 1 ether, ...)` triggers `_checkIfDepositAmountExceedesCurrentLimit`: `100_010 + 1 > 100_000` → `true`.
6. `_beforeDeposit()` reverts with `MaximumDepositLimitReached`.
7. All stETH deposits are frozen. Admin must raise the limit to restore functionality, at which point the attacker can repeat the attack. [6](#0-5) [7](#0-6)

### Citations

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

**File:** contracts/LRTDepositPool.sol (L444-444)
```text
        assetLyingInDepositPool = IERC20(asset).balanceOf(address(this));
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

**File:** contracts/LRTOracle.sol (L341-343)
```text
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```
