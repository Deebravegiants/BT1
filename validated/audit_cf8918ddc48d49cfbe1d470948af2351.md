Looking at the exact code path:

1. `NodeDelegator.getEffectivePodShares()` calls `NodeDelegatorHelper.getWithdrawableShare()` which calls `DelegationManager.getWithdrawableShares()` — not `stakerDepositShares` directly, but EigenLayer's `getWithdrawableShares` for the beaconChainETH strategy internally uses `stakerDepositShares`, which returns 0 when `podOwnerDepositShares` is negative.

2. `getEffectivePodShares()` returns `stakedButUnverifiedNativeETH + withdrawableShare`. When `withdrawableShare = 0` (negative shares clamped), the deficit is silently dropped.

3. `LRTDepositPool.getETHDistributionData()` sums `getEffectivePodShares()` across all NDCs, feeding into `LRTOracle._getTotalEthInProtocol()` → `rsETHPrice`.

The overcounting is real but bounded: it equals `|podOwnerDepositShares|` (the deficit). The price inflation is `deficit / rsETH_supply`. The downside protection in `_updateRsETHPrice()` would trigger a pause if the price drop from the previous `highestRsethPrice` exceeds `pricePercentageLimit` — but the overcounting makes the drop appear smaller than it truly is, potentially suppressing the pause trigger.

---

### Title
Beacon-chain slashing deficit silently dropped in `getEffectivePodShares`, inflating rsETHPrice above true backing — (`contracts/NodeDelegator.sol`)

### Summary
When a NodeDelegator's verified validators are slashed severely enough to drive `podOwnerDepositShares` negative, `DelegationManager.getWithdrawableShares` returns 0 (clamped). `NodeDelegator.getEffectivePodShares` then returns only `stakedButUnverifiedNativeETH`, discarding the negative-share deficit entirely. This causes `LRTOracle` to overcount ETH in the protocol and store an `rsETHPrice` above the true backing ratio.

### Finding Description

`NodeDelegator.getEffectivePodShares` is:

```solidity
// contracts/NodeDelegator.sol:556-562
function getEffectivePodShares() external view override returns (uint256 ethStaked) {
    uint256 withdrawableShare =
        NodeDelegatorHelper.getWithdrawableShare(lrtConfig, IStrategy(lrtConfig.beaconChainETHStrategy()));

    // staker balances can no longer be negative
    return stakedButUnverifiedNativeETH + withdrawableShare;
}
``` [1](#0-0) 

`NodeDelegatorHelper.getWithdrawableShare` delegates to `DelegationManager.getWithdrawableShares`:

```solidity
// contracts/NodeDelegatorHelper.sol:52-65
(withdrawableShares,) = getDelegationManager(lrtConfig).getWithdrawableShares(address(this), strategies);
``` [2](#0-1) 

EigenLayer's `DelegationManager.getWithdrawableShares` for the beaconChainETH strategy internally calls `IShareManager.stakerDepositShares`, which is documented to return 0 when `podOwnerDepositShares` is negative:

```solidity
// contracts/external/eigenlayer/interfaces/IShareManager.sol:43-44
/// @dev returns 0 if the user has negative shares
function stakerDepositShares(address user, IStrategy strategy) external view returns (uint256 depositShares);
``` [3](#0-2) 

`IEigenPodManager` also documents this:

```solidity
// contracts/external/eigenlayer/interfaces/IEigenPodManager.sol:157-160
/// @dev returns 0 if the user has negative shares.
function stakerDepositShares(address user, IStrategy strategy) external view returns (uint256 depositShares);
``` [4](#0-3) 

The negative `podOwnerDepositShares` value (the deficit) is therefore silently discarded. `getEffectivePodShares` returns `stakedButUnverifiedNativeETH` as if the deficit does not exist.

This feeds directly into `LRTDepositPool.getETHDistributionData`: [5](#0-4) 

Which feeds into `LRTOracle._getTotalEthInProtocol` → `rsETHPrice`: [6](#0-5) 

The stored `rsETHPrice` is then used by `LRTWithdrawalManager.getExpectedAssetAmount` to compute how much ETH a user receives per rsETH burned: [7](#0-6) 

### Impact Explanation

The overcounting equals `|podOwnerDepositShares|` (the deficit). `rsETHPrice` is inflated by `deficit / rsETH_supply`. Users who initiate withdrawals while the inflated price is stored receive more ETH per rsETH than the protocol can actually back. Later withdrawers receive proportionally less, violating the invariant that all rsETH holders are backed equally. No funds leave the system externally, but the distribution among holders is distorted — matching the **Low: Contract fails to deliver promised returns, but doesn't lose value** scope.

A secondary effect: the downside protection in `_updateRsETHPrice` pauses the protocol when `newRsETHPrice < highestRsethPrice` by more than `pricePercentageLimit`. The overcounting makes the computed price drop appear smaller than the true drop, potentially suppressing the automatic pause that would otherwise protect users. [8](#0-7) 

### Likelihood Explanation

Beacon-chain slashing is a known production risk. `podOwnerDepositShares` goes negative specifically when a withdrawal was queued before a checkpoint that records a large slashing loss — a realistic sequence during a correlated slashing event. Having `stakedButUnverifiedNativeETH > 0` simultaneously (i.e., some validators staked but not yet credential-verified) is normal operational state. The combination is unlikely to be common but is entirely plausible in production.

### Recommendation

In `getEffectivePodShares`, read `podOwnerDepositShares` directly from `IEigenPodManager` and subtract any negative deficit from `stakedButUnverifiedNativeETH`:

```solidity
function getEffectivePodShares() external view override returns (uint256 ethStaked) {
    uint256 withdrawableShare =
        NodeDelegatorHelper.getWithdrawableShare(lrtConfig, IStrategy(lrtConfig.beaconChainETHStrategy()));

    int256 depositShares = _getEigenPodManager().podOwnerDepositShares(address(this));
    if (depositShares < 0) {
        uint256 deficit = uint256(-depositShares);
        return stakedButUnverifiedNativeETH > deficit
            ? stakedButUnverifiedNativeETH - deficit + withdrawableShare
            : 0;
    }
    return stakedButUnverifiedNativeETH + withdrawableShare;
}
```

### Proof of Concept

```solidity
// Unit test (Foundry, fork or mock)
// 1. Deploy NDC with mock EigenPodManager and DelegationManager
// 2. Set stakedButUnverifiedNativeETH = 32 ether (one unverified validator)
// 3. Mock DelegationManager.getWithdrawableShares to return [0]
//    (simulating podOwnerDepositShares = -10 ether after slashing)
// 4. Mock EigenPodManager.podOwnerDepositShares to return -10 ether
// 5. Call getEffectivePodShares() → returns 32 ether
// 6. True backing = 32 ether - 10 ether = 22 ether
// 7. Assert rsETHPrice computed from 32 ether > rsETHPrice from 22 ether
//    → confirms inflation of ~45% above true backing in this example
```

### Citations

**File:** contracts/NodeDelegator.sol (L556-562)
```text
    function getEffectivePodShares() external view override returns (uint256 ethStaked) {
        uint256 withdrawableShare =
            NodeDelegatorHelper.getWithdrawableShare(lrtConfig, IStrategy(lrtConfig.beaconChainETHStrategy()));

        // staker balances can no longer be negative
        return stakedButUnverifiedNativeETH + withdrawableShare;
    }
```

**File:** contracts/NodeDelegatorHelper.sol (L41-65)
```text
    function getWithdrawableShares(
        ILRTConfig lrtConfig,
        IStrategy[] memory strategies
    )
        internal
        view
        returns (uint256[] memory withdrawableShares)
    {
        (withdrawableShares,) = getDelegationManager(lrtConfig).getWithdrawableShares(address(this), strategies);
    }

    function getWithdrawableShare(
        ILRTConfig lrtConfig,
        IStrategy strategy
    )
        internal
        view
        returns (uint256 withdrawableShare)
    {
        IStrategy[] memory strategies = new IStrategy[](1);
        strategies[0] = strategy;

        uint256[] memory withdrawableShares = getWithdrawableShares(lrtConfig, strategies);
        return withdrawableShares[0];
    }
```

**File:** contracts/external/eigenlayer/interfaces/IShareManager.sol (L41-44)
```text
    /// @notice Returns the current shares of `user` in `strategy`
    /// @dev strategy must be beaconChainETH when talking to the EigenPodManager
    /// @dev returns 0 if the user has negative shares
    function stakerDepositShares(address user, IStrategy strategy) external view returns (uint256 depositShares);
```

**File:** contracts/external/eigenlayer/interfaces/IEigenPodManager.sol (L157-161)
```text
    /// @notice Returns the current shares of `user` in `strategy`
    /// @dev strategy must be beaconChainETH when talking to the EigenPodManager
    /// @dev returns 0 if the user has negative shares.
    function stakerDepositShares(address user, IStrategy strategy) external view returns (uint256 depositShares);
}
```

**File:** contracts/LRTDepositPool.sol (L484-493)
```text
        for (uint256 i; i < ndcsCount;) {
            ethLyingInNDCs += nodeDelegatorQueue[i].balance;

            ethStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();
            ethUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i])
                .getAssetUnstaking(LRTConstants.ETH_TOKEN);
            unchecked {
                ++i;
            }
        }
```

**File:** contracts/LRTOracle.sol (L270-282)
```text
        if (newRsETHPrice < highestRsethPrice) {
            uint256 diff = highestRsethPrice - newRsETHPrice;
            // normalizing to 1e18
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

            // if price decrease is off limit, pause the protocol (unless it's already paused)
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
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

**File:** contracts/LRTWithdrawalManager.sol (L590-594)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```
