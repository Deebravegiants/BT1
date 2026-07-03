### Title
ETH Deposit Limit Bypass via Missing Deposit Amount in Limit Check - (File: contracts/LRTDepositPool.sol)

---

### Summary

`LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit` applies an asymmetric check between ETH and ERC20 assets. For ERC20 the incoming `amount` is included in the comparison; for ETH it is not. This allows any depositor to push the protocol's ETH holdings past the configured `depositLimitByAsset` cap by exactly one deposit whenever the running total sits precisely at the limit.

---

### Finding Description

`_checkIfDepositAmountExceedesCurrentLimit` at line 676–682 of `contracts/LRTDepositPool.sol`:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← amount NOT added
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← amount IS added
}
```

For ERC20 assets the guard correctly evaluates `totalAssetDeposits + amount > limit`, so a deposit that would push the total over the cap is rejected before any state change. For ETH the guard only checks whether the **pre-deposit** total already exceeds the limit. When `totalAssetDeposits == depositLimitByAsset` the expression `totalAssetDeposits > depositLimitByAsset` evaluates to `false`, the function returns `false` (i.e. "not exceeded"), and `_beforeDeposit` proceeds to mint rsETH and accept the ETH. After the call `totalAssetDeposits` becomes `depositLimitByAsset + depositAmount`, breaching the cap.

The public entry point `depositETH` calls `_beforeDeposit` which calls this function; it is reachable by any unprivileged depositor. [1](#0-0) [2](#0-1) [3](#0-2) 

---

### Impact Explanation

The `depositLimitByAsset` cap is the protocol's primary risk-management gate for controlling how much of each asset enters EigenLayer restaking. Bypassing it for ETH means the protocol can absorb more ETH than the risk parameters allow, minting rsETH against the excess. This constitutes the protocol failing to deliver its promised deposit-cap guarantee. No funds are directly stolen and the excess is bounded to a single deposit transaction, placing this in the **Low** impact tier: *contract fails to deliver promised returns, but doesn't lose value*.

---

### Likelihood Explanation

The bypass window opens whenever `getTotalAssetDeposits(ETH_TOKEN) == depositLimitByAsset(ETH_TOKEN)` — i.e. the running total is exactly at the cap. Because `getTotalAssetDeposits` aggregates ETH across the deposit pool, all NodeDelegators, EigenLayer pod shares, the unstaking vault, and the converter, this exact-equality condition is reachable in normal operation (e.g. when the last depositor fills the cap to the wei). Any depositor who observes this state on-chain can immediately exploit it. Likelihood is **Medium** given the condition is observable and the call is permissionless. [4](#0-3) [5](#0-4) 

---

### Recommendation

Include the incoming `amount` in the ETH branch, mirroring the ERC20 branch:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    // unified check: include the incoming amount for both ETH and ERC20
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

This makes the ETH path consistent with the ERC20 path and closes the one-deposit bypass window.

---

### Proof of Concept

1. Admin sets `depositLimitByAsset(ETH_TOKEN) = 1000 ether`.
2. Depositors fill the pool until `getTotalAssetDeposits(ETH_TOKEN) == 1000 ether`.
3. Attacker calls `depositETH{value: 100 ether}(minRSETH, "")`.
4. Inside `_checkIfDepositAmountExceedesCurrentLimit`:
   - `totalAssetDeposits = 1000 ether`
   - ETH branch: `1000 ether > 1000 ether` → `false` → check passes.
5. `_mintRsETH` mints rsETH for the attacker; the 100 ETH is accepted.
6. `getTotalAssetDeposits(ETH_TOKEN)` is now `1100 ether`, 10 % above the intended cap.
7. Subsequent depositors are correctly blocked (`1100 > 1000` → `true`), but the damage is done. [1](#0-0) [6](#0-5)

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

**File:** contracts/LRTDepositPool.sol (L467-500)
```text
    function getETHDistributionData()
        public
        view
        override
        returns (
            uint256 ethLyingInDepositPool,
            uint256 ethLyingInNDCs,
            uint256 ethStakedInEigenLayer,
            uint256 ethUnstakingFromEigenLayer,
            uint256 ethLyingInConverter,
            uint256 ethLyingInUnstakingVault
        )
    {
        ethLyingInDepositPool = address(this).balance;

        uint256 ndcsCount = nodeDelegatorQueue.length;

        for (uint256 i; i < ndcsCount;) {
            ethLyingInNDCs += nodeDelegatorQueue[i].balance;

            ethStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();
            ethUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i])
                .getAssetUnstaking(LRTConstants.ETH_TOKEN);
            unchecked {
                ++i;
            }
        }

        address lrtUnstakingVault = lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT);
        ethLyingInUnstakingVault = lrtUnstakingVault.balance;

        address lrtConverter = lrtConfig.getContract(LRTConstants.LRT_CONVERTER);
        ethLyingInConverter = ILRTConverter(lrtConverter).ethValueInWithdrawal();
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
