### Title
Unbounded Gas Consumption in `updateRSETHPrice()`, `depositETH()`, `depositAsset()`, and `initiateWithdrawal()` Due to Nested Loops Over Assets, NDCs, and Queued EigenLayer Withdrawals — (File: `contracts/LRTOracle.sol`, `contracts/LRTDepositPool.sol`, `contracts/NodeDelegator.sol`)

---

### Summary

A deeply nested, unbounded loop chain exists across `LRTOracle`, `LRTDepositPool`, and `NodeDelegator`. The public `updateRSETHPrice()` function, as well as user-facing `depositETH()`, `depositAsset()`, and `initiateWithdrawal()`, all ultimately invoke `getTotalAssetDeposits()` → `getAssetDistributionData()` → `getAssetUnstaking()`, which performs external calls to EigenLayer for every NDC and every queued withdrawal. As the protocol grows (more supported assets, more NDCs, more queued EigenLayer withdrawals), these call chains can exceed the Ethereum block gas limit, causing permanent or temporary DoS of core protocol functions.

---

### Finding Description

The call chain is:

**Path 1 (public oracle update):**
`LRTOracle.updateRSETHPrice()` → `_updateRsETHPrice()` → `_getTotalEthInProtocol()` → for each asset in `supportedAssetList`: `ILRTDepositPool.getTotalAssetDeposits(asset)` → `getAssetDistributionData(asset)` → for each NDC in `nodeDelegatorQueue`: `INodeDelegator.getAssetUnstaking(asset)` → `IDelegationManager.getQueuedWithdrawals(ndc)` → nested loop over all queued withdrawals and their strategies.

**Path 2 (user deposit):**
`LRTDepositPool.depositETH()` / `depositAsset()` → `_beforeDeposit()` → `getTotalAssetDeposits()` → same chain as above.

**Path 3 (user withdrawal initiation):**
`LRTWithdrawalManager.initiateWithdrawal()` → `getAvailableAssetAmount()` → `ILRTDepositPool.getTotalAssetDeposits()` → same chain.

**Root cause in `_getTotalEthInProtocol()`** — outer loop over all supported assets: [1](#0-0) 

**Root cause in `getAssetDistributionData()`** — inner loop over all NDCs, with two external EigenLayer calls per NDC per asset: [2](#0-1) 

**Root cause in `getAssetUnstaking()`** — a further nested loop over all queued withdrawals and their strategies per NDC: [3](#0-2) 

**`updateRSETHPrice()` is unrestricted (public, no role check):** [4](#0-3) 

**User-facing deposit entry point:** [5](#0-4) 

**User-facing withdrawal initiation entry point:** [6](#0-5) 

The combined iteration depth is: `|supportedAssets|` × `|nodeDelegatorQueue|` × `|queuedWithdrawals per NDC|` × `|strategies per withdrawal|`. Each leaf call is an external call to EigenLayer contracts. The protocol's own configuration allows up to `maxNodeDelegatorLimit` NDCs (default 10, admin-adjustable upward) and up to `maxUncompletedWithdrawalCount` = 80 total queued withdrawals. With ~5 supported assets, 10 NDCs, and 80 queued withdrawals distributed across NDCs, the number of external calls in a single transaction can reach into the hundreds to thousands, each consuming thousands of gas units. [7](#0-6) 

---

### Impact Explanation

**Medium — Unbounded gas consumption / Temporary freezing of funds.**

1. **`updateRSETHPrice()` DoS**: If the gas cost of `_getTotalEthInProtocol()` exceeds the block gas limit, no one can update the rsETH price. A stale price means: (a) protocol fee accrual halts (theft of unclaimed yield), (b) the automatic price-drop pause mechanism in `_updateRsETHPrice()` cannot trigger, removing a critical safety circuit breaker.

2. **Deposit DoS**: `depositETH()` and `depositAsset()` call `_beforeDeposit()` → `getTotalAssetDeposits()` → the same nested loop. If this reverts, all user deposits are temporarily frozen.

3. **Withdrawal initiation DoS**: `initiateWithdrawal()` calls `getAvailableAssetAmount()` → `getTotalAssetDeposits()` → same chain. Users cannot queue withdrawals. [8](#0-7) 

---

### Likelihood Explanation

**Medium.** The protocol is designed to scale: more LSTs can be added via `addNewSupportedAsset()`, more NDCs via `addNodeDelegatorContractToQueue()`, and EigenLayer queued withdrawals accumulate during normal operations (undelegation, unstaking). No attacker action is required — natural protocol growth causes the gas cost to grow monotonically. The `maxNodeDelegatorLimit` can be raised by admin, and `maxUncompletedWithdrawalCount` is capped at 80. Even at current conservative limits (10 NDCs × 5 assets × moderate queued withdrawals), the gas cost is already substantial. As the protocol scales to more assets and NDCs, the block gas limit will be breached. [9](#0-8) 

---

### Recommendation

1. **Decouple price computation from per-NDC EigenLayer queries**: Cache `totalAssetDeposits` per asset in storage and update it lazily (on deposit/withdrawal events) rather than recomputing it on every `updateRSETHPrice()` call.

2. **Paginate `getAssetDistributionData()`**: Accept a start/end NDC index so operators can update the price in batches.

3. **Remove `getAssetUnstaking()` from the hot path**: Track unstaking amounts in storage (incremented/decremented on `initiateUnstaking`/`completeUnstaking`) rather than querying EigenLayer's `getQueuedWithdrawals()` on every price update.

4. **Bound `maxNodeDelegatorLimit` with a hard cap** that accounts for the gas cost of the nested loop.

---

### Proof of Concept

```
Scenario: 5 supported assets, 10 NDCs, 8 queued withdrawals per NDC (80 total), 2 strategies per withdrawal.

updateRSETHPrice() call:
  _getTotalEthInProtocol():
    for each of 5 assets:
      getTotalAssetDeposits(asset):
        getAssetDistributionData(asset):
          for each of 10 NDCs:
            getAssetBalance(asset)       → 1 external call to EigenLayer strategy
            getAssetUnstaking(asset):
              getQueuedWithdrawals(ndc)  → 1 external call returning 8 withdrawals
              for each of 8 withdrawals:
                for each of 2 strategies: → 2 reads + sharesToUnderlyingView call

Total external calls ≈ 5 × 10 × (1 + 1 + 8×2) = 5 × 10 × 18 = 900 external calls

At ~5,000–20,000 gas per external call, total gas ≈ 4.5M–18M gas for the loop alone,
before accounting for base costs, memory expansion, and EigenLayer internal logic.
As NDC count or queued withdrawals grow, this exceeds Ethereum's 30M block gas limit.
``` [10](#0-9) [11](#0-10)

### Citations

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

**File:** contracts/LRTDepositPool.sol (L302-323)
```text
    function addNodeDelegatorContractToQueue(address[] calldata nodeDelegatorContracts) external onlyLRTAdmin {
        uint256 length = nodeDelegatorContracts.length;
        if (nodeDelegatorQueue.length + length > maxNodeDelegatorLimit) {
            revert MaximumNodeDelegatorLimitReached();
        }

        for (uint256 i; i < length;) {
            UtilLib.checkNonZeroAddress(nodeDelegatorContracts[i]);

            // check if node delegator contract is already added and add it if not
            if (isNodeDelegator[nodeDelegatorContracts[i]] == 0) {
                nodeDelegatorQueue.push(nodeDelegatorContracts[i]);
                emit NodeDelegatorAddedinQueue(nodeDelegatorContracts[i]);
            }

            isNodeDelegator[nodeDelegatorContracts[i]] = 1;

            unchecked {
                ++i;
            }
        }
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

**File:** contracts/LRTUnstakingVault.sol (L150-158)
```text
    function setMaxUncompletedWithdrawalCount(uint256 _maxUncompletedWithdrawalCount) external onlyLRTManager {
        // 120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price
        // Need buffer for theoretical operator forced undelegations (ndc count * asset count = 15)
        if (_maxUncompletedWithdrawalCount > 80) {
            revert MaxUncompletedWithdrawalCountTooHigh();
        }
        maxUncompletedWithdrawalCount = _maxUncompletedWithdrawalCount;

        emit MaxUncompletedWithdrawalCountSet(_maxUncompletedWithdrawalCount);
```
