### Title
Unbounded `minAmountToDeposit` and `depositLimitByAsset` Parameters Can Temporarily Freeze All User Deposits - (File: contracts/LRTDepositPool.sol, contracts/LRTConfig.sol)

### Summary
`LRTDepositPool.setMinAmountToDeposit()` accepts any `uint256` value with no upper bound, and `LRTConfig.updateAssetDepositLimit()` accepts any `uint256` value with no lower bound (including 0). Either misconfiguration causes every call to `depositETH` or `depositAsset` to revert, temporarily freezing all user deposits into the protocol.

### Finding Description

**Root cause 1 — `LRTDepositPool.setMinAmountToDeposit()` (no upper bound)** [1](#0-0) 

The function writes `minAmountToDeposit` without any ceiling check. If set to `type(uint256).max`, the guard in `_beforeDeposit` will always revert: [2](#0-1) 

Every call to `depositETH` or `depositAsset` will hit `InvalidAmountToDeposit` regardless of the amount supplied.

**Root cause 2 — `LRTConfig.updateAssetDepositLimit()` (no lower bound)** [3](#0-2) 

The function writes `depositLimitByAsset[asset]` without any floor check. Setting it to `0` causes `_checkIfDepositAmountExceedesCurrentLimit` to return `true` for every deposit: [4](#0-3) 

Because `totalAssetDeposits + amount > 0` is always true once any deposits exist, every subsequent call to `depositAsset` (or `depositETH` for the ETH asset) reverts with `MaximumDepositLimitReached`.

Note: `_addNewSupportedAsset` correctly rejects a zero `depositLimit` at asset-addition time, but `updateAssetDepositLimit` has no equivalent guard: [5](#0-4) 

### Impact Explanation
All user-facing deposit entry points (`depositETH`, `depositAsset`) pass through `_beforeDeposit`, which enforces both `minAmountToDeposit` and `depositLimitByAsset`. A single misconfigured call to either setter immediately blocks 100 % of new deposits into the L1 protocol, preventing users from obtaining rsETH. Because the admin can reverse the change, the freeze is temporary — matching the **Medium / Temporary freezing of funds** impact tier.

### Likelihood Explanation
Both setters are callable by privileged roles (`onlyLRTAdmin` and `MANAGER` respectively) without any timelock on the parameter values themselves. An accidental fat-finger (e.g., passing `0` instead of a new limit, or passing a value in the wrong unit) is a realistic operational error. The absence of any on-chain guardrail means there is no last-resort protection against such mistakes.

### Recommendation
1. In `setMinAmountToDeposit`, add a reasonable maximum ceiling (e.g., `require(minAmountToDeposit_ <= MAX_MIN_DEPOSIT)`).
2. In `updateAssetDepositLimit`, add a non-zero floor check identical to the one already present in `_addNewSupportedAsset`:
   ```solidity
   if (depositLimit == 0) revert InvalidDepositLimit();
   ```
3. Consider emitting the old value alongside the new value in both events to aid off-chain monitoring.

### Proof of Concept

**Scenario A — `minAmountToDeposit` set to `type(uint256).max`:**
1. Admin calls `LRTDepositPool.setMinAmountToDeposit(type(uint256).max)`.
2. User calls `depositETH{value: 1 ether}(0, "")`.
3. `_beforeDeposit` evaluates `1 ether < type(uint256).max` → `true` → reverts `InvalidAmountToDeposit`.
4. All deposits are blocked until the admin corrects the value.

**Scenario B — `depositLimitByAsset` set to `0`:**
1. Manager calls `LRTConfig.updateAssetDepositLimit(stETH, 0)`.
2. User calls `depositAsset(stETH, 1e18, 0, "")`.
3. `_checkIfDepositAmountExceedesCurrentLimit` evaluates `totalDeposits + 1e18 > 0` → `true` → reverts `MaximumDepositLimitReached`.
4. All stETH deposits are blocked until the manager corrects the limit. [6](#0-5)

### Citations

**File:** contracts/LRTDepositPool.sol (L282-285)
```text
    function setMinAmountToDeposit(uint256 minAmountToDeposit_) external onlyLRTAdmin {
        minAmountToDeposit = minAmountToDeposit_;
        emit MinAmountToDepositUpdated(minAmountToDeposit_);
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

**File:** contracts/LRTConfig.sol (L106-118)
```text
    function _addNewSupportedAsset(address asset, uint256 depositLimit) private {
        UtilLib.checkNonZeroAddress(asset);
        if (depositLimit == 0) {
            revert InvalidDepositLimit();
        }
        if (isSupportedAsset[asset]) {
            revert AssetAlreadySupported();
        }
        isSupportedAsset[asset] = true;
        supportedAssetList.push(asset);
        depositLimitByAsset[asset] = depositLimit;
        emit AddedNewSupportedAsset(asset, depositLimit);
    }
```

**File:** contracts/LRTConfig.sol (L123-133)
```text
    function updateAssetDepositLimit(
        address asset,
        uint256 depositLimit
    )
        external
        onlyRole(LRTConstants.MANAGER)
        onlySupportedAsset(asset)
    {
        depositLimitByAsset[asset] = depositLimit;
        emit AssetDepositLimitUpdate(asset, depositLimit);
    }
```
