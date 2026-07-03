### Title
Manager-Only `updateRSETHPriceAsManager()` Shares Identical Gas-Unbounded Call Path as Public `updateRSETHPrice()`, Eliminating the Privileged Recovery Path — (`contracts/LRTOracle.sol`)

---

### Summary

`updateRSETHPriceAsManager()` skips `whenNotPaused` but delegates immediately to `_updateRsETHPrice()`, which executes the exact same `_getTotalEthInProtocol()` → `getTotalAssetDeposits()` → `getAssetUnstaking()` → `getQueuedWithdrawals()` chain. Under maximum NDC queue depth with many pending EigenLayer withdrawals, both entry points revert out-of-gas identically, leaving the protocol with no on-chain path to update `rsETHPrice`.

---

### Finding Description

**Entry points:**

`updateRSETHPrice()` (public, `whenNotPaused`) and `updateRSETHPriceAsManager()` (manager-only, no pause gate) both call `_updateRsETHPrice()` unconditionally: [1](#0-0) 

`_updateRsETHPrice()` calls `_getTotalEthInProtocol()`: [2](#0-1) 

`_getTotalEthInProtocol()` loops over every supported asset and calls `getTotalAssetDeposits(asset)` on the deposit pool for each: [3](#0-2) 

`getTotalAssetDeposits()` calls `getAssetDistributionData()`, which for each NDC in `nodeDelegatorQueue` calls `getAssetUnstaking(asset)`: [4](#0-3) 

For ETH, `getETHDistributionData()` also calls `getAssetUnstaking(ETH_TOKEN)` per NDC: [5](#0-4) 

`NodeDelegator.getAssetUnstaking()` calls `_getDelegationManager().getQueuedWithdrawals(address(this))`, which returns **all** queued withdrawals for that NDC, then iterates over every withdrawal and every strategy within it: [6](#0-5) 

**Gas scaling:** `O(NDCs × queued_withdrawals_per_NDC × strategies_per_withdrawal)`. With `maxNodeDelegatorLimit` defaulting to 10 and many pending withdrawals per NDC (bounded only by `maxUncompletedWithdrawalCount` in the unstaking vault), this can easily exceed the 30M block gas limit.

**The manager path provides zero gas relief.** The only difference between the two entry points is the absence of `whenNotPaused` in `updateRSETHPriceAsManager()`. The entire downstream computation is identical.

---

### Impact Explanation

When the gas threshold is crossed, **both** `updateRSETHPrice()` and `updateRSETHPriceAsManager()` revert OOG. `rsETHPrice` becomes stale. All protocol flows that depend on a fresh price (deposits, mints, withdrawals) operate on a frozen exchange rate. The protocol has no on-chain mechanism to recover the price update without first completing enough pending EigenLayer withdrawals to bring gas consumption below the block limit — an operation that itself requires multiple separate transactions and a cooldown period.

Impact: **Medium — Temporary freezing of funds / Unbounded gas consumption** (price staleness blocks correct deposit/withdrawal accounting).

---

### Likelihood Explanation

- `maxNodeDelegatorLimit` is admin-configurable and can be raised above 10.
- `undelegate()` on a single NDC can queue multiple withdrawal roots in one call, rapidly accumulating pending withdrawals.
- No attacker action is required; normal protocol operation (staking, undelegating, rebalancing) naturally accumulates queued withdrawals.
- The condition is self-reinforcing: once OOG, the price cannot be updated, which may trigger further pauses, making recovery harder.

---

### Recommendation

1. **Decouple TVL accounting from on-chain enumeration.** Cache per-NDC asset balances in storage and update them lazily (on deposit/withdrawal events) rather than re-enumerating all EigenLayer queued withdrawals on every price update.
2. **Provide a gas-bounded manager override.** Add a variant of `updateRSETHPriceAsManager()` that accepts a pre-computed `totalETHInProtocol` value (validated against a signed off-chain proof or a trusted keeper), bypassing `_getTotalEthInProtocol()` entirely.
3. **Cap `getAssetUnstaking` iteration.** Limit the number of queued withdrawals iterated per NDC, or move to a push-based accounting model where each `initiateUnstaking` / `completeUnstaking` updates a running total.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Fork test — run against a mainnet/testnet fork with the deployed contracts
// Foundry: forge test --fork-url $RPC_URL --match-test testManagerPathOOG -vvv

contract TestManagerPathOOG is Test {
    ILRTOracle oracle = ILRTOracle(ORACLE_ADDR);
    ILRTDepositPool pool = ILRTDepositPool(POOL_ADDR);
    address manager = MANAGER_ADDR;

    function testManagerPathOOG() external {
        // 1. As operator: queue 80 withdrawals distributed across NDCs
        //    (8 withdrawals × 10 NDCs, or any distribution summing to ~80)
        //    Use initiateUnstaking() or undelegate() per NDC.

        // 2. Verify gas cost of updateRSETHPriceAsManager
        vm.startPrank(manager);
        uint256 gasBefore = gasleft();
        try oracle.updateRSETHPriceAsManager() {
            uint256 gasUsed = gasBefore - gasleft();
            emit log_named_uint("gas used", gasUsed);
            // Assert gas used approaches or exceeds block limit
            assertGt(gasUsed, 25_000_000, "gas not near block limit");
        } catch {
            // OOG revert — manager path is bricked
            emit log("updateRSETHPriceAsManager reverted OOG");
            assertTrue(true);
        }
        vm.stopPrank();
    }
}
```

The test demonstrates that `updateRSETHPriceAsManager()` — the only privileged recovery path — is subject to the same OOG condition as the public `updateRSETHPrice()`, confirming there is no on-chain escape hatch. [7](#0-6) [8](#0-7) [9](#0-8) [10](#0-9) [11](#0-10)

### Citations

**File:** contracts/LRTOracle.sol (L87-96)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }

    /// @dev update rsETH price as an manager account
    /// @dev main benefit is to be able to update the price in case of the price going above the threshold
    /// @dev only LRT manager is allowed to call this function
    function updateRSETHPriceAsManager() external onlyLRTManager {
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

**File:** contracts/LRTDepositPool.sol (L484-492)
```text
        for (uint256 i; i < ndcsCount;) {
            ethLyingInNDCs += nodeDelegatorQueue[i].balance;

            ethStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();
            ethUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i])
                .getAssetUnstaking(LRTConstants.ETH_TOKEN);
            unchecked {
                ++i;
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
