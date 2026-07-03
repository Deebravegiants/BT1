### Title
Nested Unbounded Loops in `updateRSETHPrice()` Can Cause Permanent Gas Exhaustion - (File: contracts/LRTOracle.sol)

### Summary
`LRTOracle.updateRSETHPrice()` is a public, permissionless function that internally executes nested loops over supported assets, node delegators, queued EigenLayer withdrawals, and withdrawal strategies. As the protocol scales, the multiplicative gas cost of these nested loops can exceed the block gas limit, permanently preventing price updates and blocking protocol fee minting.

### Finding Description
`updateRSETHPrice()` calls `_getTotalEthInProtocol()`, which loops over every supported asset. For each asset, it calls `ILRTDepositPool.getTotalAssetDeposits(asset)` → `getAssetDistributionData(asset)`, which loops over every node delegator in `nodeDelegatorQueue`. For each node delegator, it calls `INodeDelegator.getAssetUnstaking(asset)`, which fetches all queued EigenLayer withdrawals via `_getDelegationManager().getQueuedWithdrawals(address(this))` and then iterates over every strategy within each withdrawal.

The call chain is:

```
updateRSETHPrice()                          [public, no access control]
  └─ _getTotalEthInProtocol()
       └─ for each supportedAsset           [loop 1: asset count]
            └─ getTotalAssetDeposits(asset)
                 └─ getAssetDistributionData(asset)
                      └─ for each NDC       [loop 2: NDC count]
                           └─ getAssetUnstaking(asset)
                                └─ for each queuedWithdrawal   [loop 3: withdrawal count]
                                     └─ for each strategy      [loop 4: strategy count]
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

The protocol itself acknowledges this concern in `LRTUnstakingVault.setMaxUncompletedWithdrawalCount()`:

```solidity
// 120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price
if (_maxUncompletedWithdrawalCount > 80) {
    revert MaxUncompletedWithdrawalCountTooHigh();
}
``` [5](#0-4) 

However, the cap on `maxUncompletedWithdrawalCount` (≤ 80) does not fully bound the total gas because the cost is multiplicative: `supportedAssets.length × nodeDelegatorQueue.length × queuedWithdrawals.length × strategies.length`. With `maxNodeDelegatorLimit` initialized to 10 and multiple supported assets, the combined iteration count can still grow to exceed block gas limits. Furthermore, `getQueuedWithdrawals()` reads directly from EigenLayer's `DelegationManager`, which is not bounded by the protocol's internal counter — forced undelegations or other EigenLayer-side events can increase the actual queued withdrawal count beyond what the protocol tracks.

### Impact Explanation
If `updateRSETHPrice()` becomes uncallable due to gas exhaustion:
1. The stored `rsETHPrice` becomes permanently stale.
2. Protocol fee minting (inside `_updateRsETHPrice()`) is permanently blocked — this is a **permanent freezing of unclaimed yield** (Medium).
3. The withdrawal system's `getExpectedAssetAmount()` reads `lrtOracle.rsETHPrice()` for the stale stored value, causing incorrect withdrawal rates for all users.

### Likelihood Explanation
The protocol already caps `maxUncompletedWithdrawalCount` at 80 precisely because of this concern, demonstrating the risk is real and recognized. As the protocol grows (more supported assets, more NDCs, more EigenLayer withdrawal activity), the multiplicative gas cost approaches block limits. Any operator-triggered undelegation event that creates many withdrawal roots simultaneously (e.g., `undelegate()` emitting multiple `withdrawalRoots`) can spike the queued withdrawal count beyond the protocol's internal tracking. [6](#0-5) 

### Recommendation
1. Cache the result of `getAssetUnstaking()` off-chain and provide it as a parameter to `updateRSETHPrice()`, or split the price update into per-asset batches.
2. Introduce a hard cap on the number of supported assets and node delegators that is enforced with the gas budget of `updateRSETHPrice()` in mind.
3. Consider separating the fee-minting logic from the price-update loop so that fee minting can proceed even if the full TVL computation is expensive.

### Proof of Concept
1. Protocol has 3 supported assets, 10 NDCs, and 80 queued EigenLayer withdrawals each with 5 strategies.
2. Any address calls `updateRSETHPrice()`.
3. `_getTotalEthInProtocol()` executes: 3 × 10 × 80 × 5 = 12,000 iterations, each involving external `STATICCALL`s to EigenLayer strategy contracts.
4. Gas consumption exceeds the block gas limit (~30M on Ethereum mainnet).
5. The transaction reverts. `rsETHPrice` is never updated. Protocol fee minting is permanently blocked. [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L214-232)
```text
    function _updateRsETHPrice() internal {
        address rsETHTokenAddress = lrtConfig.rsETH();
        uint256 rsethSupply = IRSETH(rsETHTokenAddress).totalSupply();

        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }

        if (highestRsethPrice == 0) {
            highestRsethPrice = rsETHPrice;
        }

        uint256 previousPrice = rsETHPrice;

        // get total ETH in the protocol (normalized to 1e18)
        uint256 totalETHInProtocol = _getTotalEthInProtocol();

```

**File:** contracts/LRTOracle.sol (L298-316)
```text
        // mint protocol fee as rsETH if there's a fee to take
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
            }
        } else {
            _checkAndUpdateDailyFeeMintLimit(0);
        }

        rsETHPrice = newRsETHPrice;

        emit RsETHPriceUpdate(rsETHPrice, previousPrice);
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

**File:** contracts/NodeDelegator.sol (L264-288)
```text
    function undelegate() external whenNotPaused onlyLRTManager {
        if (elOperatorDelegatedTo() == address(0)) {
            revert CantUndelegate();
        }

        bytes32[] memory withdrawalRoots = _getDelegationManager().undelegate(address(this));

        if (
            _getUnstakingVault().uncompletedWithdrawalCount() + withdrawalRoots.length
                > _getUnstakingVault().maxUncompletedWithdrawalCount()
        ) {
            revert MaxUncompletedWithdrawalsReached();
        }

        for (uint256 i; i < withdrawalRoots.length; i++) {
            _getUnstakingVault().increaseUncompletedWithdrawalCount();

            // NOTE: For legacy event emission we emit single withdrawal roots
            bytes32[] memory singleWithdrawal = new bytes32[](1);
            singleWithdrawal[0] = withdrawalRoots[i];
            emit WithdrawalQueued(_getNonce() - withdrawalRoots.length + i, address(this), singleWithdrawal);
        }

        emit Undelegated();
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

**File:** contracts/LRTUnstakingVault.sol (L151-158)
```text
        // 120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price
        // Need buffer for theoretical operator forced undelegations (ndc count * asset count = 15)
        if (_maxUncompletedWithdrawalCount > 80) {
            revert MaxUncompletedWithdrawalCountTooHigh();
        }
        maxUncompletedWithdrawalCount = _maxUncompletedWithdrawalCount;

        emit MaxUncompletedWithdrawalCountSet(_maxUncompletedWithdrawalCount);
```
