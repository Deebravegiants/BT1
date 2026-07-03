### Title
ETH Deposit Limit Check Omits Incoming Amount, Allowing Configured Cap to Be Exceeded - (File: contracts/LRTDepositPool.sol)

### Summary
`LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit` contains an ETH-specific branch that checks `totalAssetDeposits > depositLimit` without including the incoming deposit amount, while the ERC20 branch correctly checks `totalAssetDeposits + amount > depositLimit`. The ETH-specific hardcoded branch short-circuits and returns before the amount-inclusive check can be applied, meaning the configured ETH deposit cap is never properly enforced for ETH depositors.

### Finding Description
The structural parallel to the reported fallback-handler ordering bug is exact: a hardcoded type-specific branch executes first and returns early, preventing the correct configurable-path logic from ever running.

In `ModuleManager.sol` (original report), NFT receiver selectors were matched before custom fallback handlers were consulted, so custom handlers for those selectors never executed. In `LRTDepositPool`, the ETH token address is matched first and a weaker check is returned, so the correct amount-inclusive limit check never executes for ETH. [1](#0-0) 

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)); // ← `amount` never added
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← correct for ERC20
}
```

The ETH branch returns `totalAssetDeposits > depositLimit`. This means:

1. When `totalAssetDeposits == depositLimit` (limit exactly reached), the check returns `false` (not exceeded), allowing further ETH deposits.
2. When `totalAssetDeposits < depositLimit` but `totalAssetDeposits + msg.value > depositLimit`, the check also returns `false`, allowing a deposit that would push the total beyond the cap.

This function is called unconditionally from `_beforeDeposit`, which is called by `depositETH`. [2](#0-1) 

### Impact Explanation
The ETH deposit limit set by the admin via `lrtConfig.depositLimitByAsset(ETH_TOKEN)` is not enforced for ETH deposits. Any depositor can push total ETH deposits beyond the configured cap. The deposit limit is a promised protocol constraint (risk management ceiling); bypassing it means the contract fails to deliver its promised deposit-cap guarantee for ETH.

**Impact: Low — Contract fails to deliver promised returns.**

### Likelihood Explanation
High. Any unprivileged depositor calling `depositETH` triggers this path. No special role, front-running, or external dependency is required. The only precondition is that the protocol is unpaused and a deposit limit has been set.

### Recommendation
Change the ETH branch to include the incoming deposit amount, consistent with the ERC20 branch:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

### Proof of Concept
1. Admin sets ETH deposit limit to 1000 ETH: `lrtConfig.updateAssetDepositLimit(ETH_TOKEN, 1000 ether)`.
2. Legitimate deposits accumulate until `getTotalAssetDeposits(ETH_TOKEN) == 1000 ether`.
3. Attacker calls `depositETH{value: 100 ether}(0, "")`.
4. `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, 100 ether)` is invoked.
5. ETH branch evaluates: `1000 ether > 1000 ether` → `false` (not exceeded).
6. `_beforeDeposit` does not revert; deposit proceeds.
7. Total ETH deposits become 1100 ETH, 10% above the configured cap, with rsETH minted for the excess. [3](#0-2) [4](#0-3)

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
