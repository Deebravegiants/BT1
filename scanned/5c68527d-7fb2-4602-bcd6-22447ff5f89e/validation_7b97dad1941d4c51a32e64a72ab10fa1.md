### Title
Stale Cached `rsETHPrice` Read in Deposit and Withdrawal Functions Without Prior Update — (`contracts/LRTDepositPool.sol`, `contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTOracle.rsETHPrice` is a stored state variable that is only refreshed when `updateRSETHPrice()` is explicitly called. Both `LRTDepositPool.getRsETHAmountToMint()` and `LRTWithdrawalManager.getExpectedAssetAmount()` read `lrtOracle.rsETHPrice()` directly without triggering an update first. When EigenLayer rewards accrue and the true rsETH value rises above the cached price, a depositor receives more rsETH than deserved, diluting existing holders' accrued yield.

---

### Finding Description

`LRTOracle` stores the rsETH/ETH exchange rate in the state variable `rsETHPrice`. [1](#0-0) 

This value is only updated when `updateRSETHPrice()` (public, `whenNotPaused`) or `updateRSETHPriceAsManager()` (manager-only) is called: [2](#0-1) 

The deposit path reads this cached value directly without first calling an update: [3](#0-2) 

The withdrawal initiation path does the same: [4](#0-3) 

Both `depositETH()` and `depositAsset()` call `_beforeDeposit()` → `getRsETHAmountToMint()`, which divides by the stale `rsETHPrice`: [5](#0-4) 

Similarly, `initiateWithdrawal()` calls `getExpectedAssetAmount()` using the same stale price: [6](#0-5) 

---

### Impact Explanation

**High — Theft of unclaimed yield.**

When EigenLayer rewards accrue (validator rewards, restaking yield), the true rsETH/ETH ratio rises above the stored `rsETHPrice`. Until `updateRSETHPrice()` is called, the cached price is lower than the true value. A depositor calling `depositETH()` or `depositAsset()` during this window receives:

```
rsethAmountToMint = (depositAmount * assetPrice) / staleLowerRsETHPrice
```

This mints **more rsETH than the deposit is worth at the true current rate**, diluting the share of all existing rsETH holders. The attacker then calls `updateRSETHPrice()` themselves (it is public) or waits for the keeper to do so, after which they hold rsETH at the updated higher price and can withdraw more assets than they deposited. The yield that belonged to existing holders is transferred to the attacker.

---

### Likelihood Explanation

The protocol relies on off-chain keepers to call `updateRSETHPrice()` periodically. Any gap between reward accrual on EigenLayer and the keeper's next update creates the exploitable window. An attacker can monitor on-chain EigenLayer strategy balances (which feed into `_getTotalEthInProtocol()`) to detect when the true TVL has risen above `rsethSupply * rsETHPrice`, then front-run the keeper's update transaction by depositing first. This requires no special privileges and is reachable by any unprivileged depositor. [7](#0-6) 

---

### Recommendation

`depositETH()`, `depositAsset()`, and `initiateWithdrawal()` should call `updateRSETHPrice()` (or an internal equivalent) before reading `rsETHPrice`. Alternatively, `getRsETHAmountToMint()` and `getExpectedAssetAmount()` should compute the price on-the-fly from current TVL rather than reading the cached state variable.

---

### Proof of Concept

1. EigenLayer rewards accrue; `_getTotalEthInProtocol()` would now return a value higher than `rsethSupply * rsETHPrice`, but `updateRSETHPrice()` has not yet been called.
2. Attacker calls `LRTDepositPool.depositETH{value: 10 ether}(0, "")`.
3. `getRsETHAmountToMint(ETH_TOKEN, 10 ether)` executes: `rsethAmountToMint = (10e18 * 1e18) / staleLowerRsETHPrice`. Because `staleLowerRsETHPrice < trueRsETHPrice`, the attacker receives excess rsETH.
4. Attacker calls `LRTOracle.updateRSETHPrice()` (public function, no access control beyond `whenNotPaused`).
5. `rsETHPrice` is now updated to the true higher value.
6. Attacker calls `LRTWithdrawalManager.initiateWithdrawal(asset, excessRsETH, "")`, receiving `excessRsETH * newHigherRsETHPrice / assetPrice` in underlying assets — more than the original 10 ETH deposited.
7. The difference is extracted from the yield that belonged to pre-existing rsETH holders. [8](#0-7) [9](#0-8)

### Citations

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L331-349)
```text
    function _getTotalEthInProtocol() private view returns (uint256 totalETHInProtocol) {
        address lrtDepositPoolAddr = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
        address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
        uint256 supportedAssetCount = supportedAssets.length;

        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);

            unchecked {
                ++assetIdx;
            }
        }
    }
```

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

**File:** contracts/LRTDepositPool.sol (L519-520)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/LRTDepositPool.sol (L648-665)
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
```

**File:** contracts/LRTWithdrawalManager.sol (L150-178)
```text
    function initiateWithdrawal(
        address asset,
        uint256 rsETHUnstaked,
        string calldata referralId
    )
        external
        override
        nonReentrant
        whenNotPaused
        onlySupportedAsset(asset)
        onlySupportedStrategy(asset)
    {
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }

        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);

        emit ReferralIdEmitted(referralId);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L592-593)
```text
        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```
