### Title
Unbounded Nested Loop in `NodeDelegator.getAssetUnstaking()` Called from Public Deposit and Price-Update Paths Can Cause DoS - (File: contracts/NodeDelegator.sol)

---

### Summary

`NodeDelegator.getAssetUnstaking()` contains a nested loop over all EigenLayer-queued withdrawals and their strategies. This view function is invoked on every call to `LRTDepositPool.depositETH()`, `LRTDepositPool.depositAsset()`, and `LRTOracle.updateRSETHPrice()`. As the number of NDCs, queued withdrawals, and strategies per withdrawal grows — all of which are configurable by protocol operators — the cumulative gas cost of these nested loops can exceed the block gas limit, permanently reverting all deposits and price updates.

---

### Finding Description

`NodeDelegator.getAssetUnstaking()` fetches all currently queued withdrawals from EigenLayer's `DelegationManager` and iterates over them with a nested loop:

```solidity
// contracts/NodeDelegator.sol lines 405-427
function getAssetUnstaking(address asset) external view returns (uint256 amount) {
    (IDelegationManager.Withdrawal[] memory queuedWithdrawals, uint256[][] memory withdrawalShares) =
        _getDelegationManager().getQueuedWithdrawals(address(this));

    for (uint256 withdrawalIndex = 0; withdrawalIndex < queuedWithdrawals.length; withdrawalIndex++) {
        IDelegationManager.Withdrawal memory withdrawal = queuedWithdrawals[withdrawalIndex];
        for (uint256 strategyIndex = 0; strategyIndex < withdrawal.strategies.length; strategyIndex++) {
            ...
        }
    }
}
``` [1](#0-0) 

This function is called inside `LRTDepositPool.getAssetDistributionData()`, which iterates over every NDC in `nodeDelegatorQueue`:

```solidity
// contracts/LRTDepositPool.sol lines 446-456
uint256 ndcsCount = nodeDelegatorQueue.length;
for (uint256 i; i < ndcsCount;) {
    assetLyingInNDCs += IERC20(asset).balanceOf(nodeDelegatorQueue[i]);
    assetStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetBalance(asset);
    assetUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset);
    ...
}
``` [2](#0-1) 

`getAssetDistributionData()` is called by `getTotalAssetDeposits()`, which is called by `_checkIfDepositAmountExceedesCurrentLimit()` inside `_beforeDeposit()`, which is called by both `depositETH()` and `depositAsset()`: [3](#0-2) [4](#0-3) 

Additionally, `LRTOracle._getTotalEthInProtocol()` calls `getTotalAssetDeposits()` for **every supported asset**, multiplying the cost further:

```solidity
// contracts/LRTOracle.sol lines 331-349
for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
    ...
    uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
    ...
}
``` [5](#0-4) 

`_getTotalEthInProtocol()` is called by the public `updateRSETHPrice()`: [6](#0-5) 

The effective gas cost scales as:

> `supportedAssets.length × nodeDelegatorQueue.length × queuedWithdrawals.length × strategies.length`

All four dimensions are configurable: `maxNodeDelegatorLimit` (initially 10, raiseable by admin via `updateMaxNodeDelegatorLimit()`), `maxUncompletedWithdrawalCount` (set in `LRTUnstakingVault`), and the number of strategies per withdrawal (operator-supplied in `initiateUnstaking()`). [7](#0-6) 

---

### Impact Explanation

If the product of these four dimensions grows large enough to exhaust the block gas limit, every call to `depositETH()`, `depositAsset()`, and `updateRSETHPrice()` will revert. This constitutes a **temporary (potentially permanent) freezing of the deposit path** and a stale rsETH price, which also breaks the withdrawal path (since `getExpectedAssetAmount()` reads `rsETHPrice`). Existing deposited funds are not directly stolen, but the protocol becomes inoperable until the state is reduced (e.g., by completing queued withdrawals).

**Impact class**: Medium — Temporary freezing of funds / Unbounded gas consumption.

---

### Likelihood Explanation

The `maxNodeDelegatorLimit` starts at 10 and can be raised by admin. The `maxUncompletedWithdrawalCount` is a separate configurable parameter. Operators legitimately call `initiateUnstaking()` with multiple strategies. As the protocol scales (more NDCs, more concurrent unstaking operations), the combined loop depth grows organically without any malicious intent. This mirrors the original report exactly: the parameter was initially safe but could be changed to a value that triggers the DoS.

---

### Recommendation

1. **Cache `getQueuedWithdrawals()` results** or restructure `getAssetUnstaking()` to avoid fetching and iterating the full withdrawal queue on every deposit/price-update call.
2. **Decouple the accounting** of unstaking amounts from the hot deposit path. Store `assetUnstaking` as a cached state variable updated lazily (e.g., on `initiateUnstaking()` and `completeUnstaking()`) rather than recomputing it on every read.
3. **Cap the number of strategies per withdrawal** in `initiateUnstaking()` to bound the inner loop.
4. Consider the same approach recommended in the original report: store intermediate values and process them in separate transactions rather than recomputing everything inline.

---

### Proof of Concept

1. Admin raises `maxNodeDelegatorLimit` to 10 and deploys 10 NDCs.
2. Operator calls `initiateUnstaking()` on each NDC with 5 strategies, up to `maxUncompletedWithdrawalCount` times (e.g., 50 pending withdrawals per NDC).
3. Protocol supports 5 LST assets.
4. Any user calls `depositETH()`. The call chain reaches `getAssetUnstaking()` for each (asset × NDC) pair: `5 × 10 × 50 × 5 = 12,500` inner iterations, each involving external storage reads from EigenLayer. The transaction reverts with out-of-gas.
5. `updateRSETHPrice()` similarly reverts, freezing the rsETH price and breaking the withdrawal path.

### Citations

**File:** contracts/NodeDelegator.sol (L405-427)
```text
    function getAssetUnstaking(address asset) external view returns (uint256 amount) {
        (IDelegationManager.Withdrawal[] memory queuedWithdrawals, uint256[][] memory withdrawalShares) =
            _getDelegationManager().getQueuedWithdrawals(address(this));

        for (uint256 withdrawalIndex = 0; withdrawalIndex < queuedWithdrawals.length; withdrawalIndex++) {
            IDelegationManager.Withdrawal memory withdrawal = queuedWithdrawals[withdrawalIndex];

            for (uint256 strategyIndex = 0; strategyIndex < withdrawal.strategies.length; strategyIndex++) {
                IStrategy strategy = withdrawal.strategies[strategyIndex];

                address strategyAsset = address(strategy) == address(lrtConfig.beaconChainETHStrategy())
                    ? LRTConstants.ETH_TOKEN
                    : address(strategy.underlyingToken());

                if (strategyAsset != asset) continue;

                uint256 sharesToUnstake = withdrawalShares[withdrawalIndex][strategyIndex];
                amount += strategyAsset == LRTConstants.ETH_TOKEN
                    ? sharesToUnstake
                    : strategy.sharesToUnderlyingView(sharesToUnstake);
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

**File:** contracts/LRTDepositPool.sol (L290-297)
```text
    function updateMaxNodeDelegatorLimit(uint256 maxNodeDelegatorLimit_) external onlyLRTAdmin {
        if (maxNodeDelegatorLimit_ < nodeDelegatorQueue.length) {
            revert InvalidMaximumNodeDelegatorLimit();
        }

        maxNodeDelegatorLimit = maxNodeDelegatorLimit_;
        emit MaxNodeDelegatorLimitUpdated(maxNodeDelegatorLimit);
    }
```

**File:** contracts/LRTDepositPool.sol (L446-456)
```text
        uint256 ndcsCount = nodeDelegatorQueue.length;
        for (uint256 i; i < ndcsCount;) {
            assetLyingInNDCs += IERC20(asset).balanceOf(nodeDelegatorQueue[i]);

            assetStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetBalance(asset);
            assetUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset);

            unchecked {
                ++i;
            }
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
