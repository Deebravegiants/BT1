### Title
ETH Deposit Limit Bypass Due to Inconsistent Amount Check in `_checkIfDepositAmountExceedesCurrentLimit` - (File: contracts/LRTDepositPool.sol)

### Summary
`LRTDepositPool` enforces per-asset deposit caps via `depositLimitByAsset`. However, the internal check function `_checkIfDepositAmountExceedesCurrentLimit` applies two different validation logics depending on the asset type: LST deposits correctly include the incoming `amount` in the comparison, while ETH deposits completely ignore the incoming `amount`. This allows any unprivileged depositor to bypass the ETH deposit cap in a single transaction.

### Finding Description

`LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit` contains a branching check:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)); // amount ignored
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // amount included
}
``` [1](#0-0) 

For LST assets, the check is `totalAssetDeposits + amount > limit`, which correctly prevents a deposit that would push total deposits over the cap. For ETH, the check is only `totalAssetDeposits > limit`, which only blocks deposits when the cap has **already been exceeded**. The incoming `amount` is entirely discarded.

This means: if `totalAssetDeposits = 0` and `depositLimitByAsset[ETH_TOKEN] = 100 ether`, a user can call `depositETH` with `msg.value = 1_000_000 ether` and the check returns `false` (not exceeded), allowing the deposit to proceed and minting rsETH for the full amount.

The entry path is `depositETH` → `_beforeDeposit` → `_checkIfDepositAmountExceedesCurrentLimit`: [2](#0-1) [3](#0-2) 

### Impact Explanation

The `depositLimitByAsset` cap is a risk management control intended to limit the protocol's exposure to any single asset. Bypassing the ETH cap allows unlimited ETH to flow into EigenLayer strategies beyond the intended ceiling. If EigenLayer slashing events or ETH strategy failures occur at a scale beyond what the protocol sized for, the excess unbounded deposits create systematic insolvency risk. rsETH holders who deposited under the assumption that caps were enforced bear this unintended tail risk.

**Impact**: Medium — the protocol fails to enforce its own deposit limit for ETH, creating systematic risk analogous to the JUSDBank collateral cap bypass.

### Likelihood Explanation

Any unprivileged user calling `depositETH` with a large `msg.value` can trigger this in a single transaction, with no special setup required. The only precondition is that `totalAssetDeposits` has not already exceeded the limit (i.e., the cap has not been breached by prior deposits). This is the normal operating state of the protocol.

**Likelihood**: High.

### Recommendation

Apply the same `amount`-inclusive check for ETH as is used for LST assets:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

This unifies the logic and ensures the incoming deposit amount is always considered against the cap, regardless of asset type.

### Proof of Concept

1. Admin sets `depositLimitByAsset[ETH_TOKEN] = 100 ether` via `LRTConfig.updateAssetDepositLimit`.
2. Protocol starts fresh: `getTotalAssetDeposits(ETH_TOKEN) = 0`.
3. Attacker calls `LRTDepositPool.depositETH{value: 10_000 ether}(0, "")`.
4. Inside `_beforeDeposit`, `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, 10_000 ether)` is called.
5. The ETH branch executes: `return (0 > 100 ether)` → returns `false` (not exceeded).
6. The deposit proceeds; `10_000 ether` enters the protocol and rsETH is minted for the attacker.
7. The ETH deposit limit of `100 ether` has been bypassed by a factor of 100×. [1](#0-0) [4](#0-3)

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

**File:** contracts/LRTConfig.sol (L23-23)
```text
    mapping(address token => uint256 amount) public depositLimitByAsset;
```
