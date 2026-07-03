### Title
Block Stuffing Delays `sendFunds()`, Causing `updateRSETHPrice()` to Underprice rsETH by Excluding Pending MEV Rewards — (`contracts/FeeReceiver.sol`)

---

### Summary

`FeeReceiver.sendFunds()` is permissionless and must be called to move accumulated MEV/execution-layer rewards into `LRTDepositPool` before they are counted in TVL. `LRTOracle._getTotalEthInProtocol()` only counts ETH already inside the deposit pool and its downstream contracts — `FeeReceiver.balance` is explicitly excluded until `sendFunds()` is called. An attacker can use block stuffing to prevent `sendFunds()` from landing before calling `updateRSETHPrice()`, causing the oracle to record a price that is lower than the true backing per rsETH.

---

### Finding Description

`FeeReceiver.sendFunds()` has no access control: [1](#0-0) 

`LRTOracle.updateRSETHPrice()` is also fully public: [2](#0-1) 

The oracle's internal TVL calculation calls `getTotalAssetDeposits()` for every supported asset, which for ETH routes through `getETHDistributionData()`: [3](#0-2) 

`getETHDistributionData()` counts the deposit pool's own balance, NDC balances, EigenLayer pod shares, the unstaking vault, and the converter — but **never** `FeeReceiver.balance`. The code comment confirms this is intentional: [4](#0-3) [5](#0-4) 

The rsETH price is then computed as: [6](#0-5) 

If `FeeReceiver.balance > 0` at the time `updateRSETHPrice()` executes, the numerator (`totalETHInProtocol`) is understated, and `rsETHPrice` is set below its true value.

**Attack sequence:**

1. Attacker monitors `FeeReceiver.balance` accumulating MEV rewards.
2. Attacker submits a flood of high-gas-price transactions to fill the next N blocks, preventing any `sendFunds()` call from being included (block stuffing).
3. Attacker (or anyone) calls `updateRSETHPrice()` in the stuffed window.
4. Oracle records `rsETHPrice` without the pending `FeeReceiver.balance` in TVL.
5. rsETH is mispriced downward for the duration until `sendFunds()` is eventually called and the oracle is updated again.

---

### Impact Explanation

The recorded `rsETHPrice` is lower than the true backing per token by approximately `FeeReceiver.balance / rsethSupply`. During this window:

- New depositors receive more rsETH than they are entitled to (diluting existing holders).
- The protocol fails to deliver the promised exchange rate to existing rsETH holders.
- If the price drop exceeds `pricePercentageLimit`, the downside-protection logic at lines 270–282 of `LRTOracle.sol` will **pause the deposit pool and withdrawal manager**, escalating the impact to a temporary freeze. [7](#0-6) 

**Scoped impact:** Low — contract fails to deliver promised returns; secondary risk of temporary fund freeze if the mispricing crosses the pause threshold.

---

### Likelihood Explanation

Block stuffing on Ethereum mainnet is expensive but has been executed in practice (e.g., against time-sensitive oracle windows). The cost scales with the number of blocks that must be stuffed and the prevailing base fee. MEV rewards accumulate continuously; a large enough balance makes the attack economically rational. Both `sendFunds()` and `updateRSETHPrice()` are permissionless, so the attacker controls both sides of the timing race without needing any privileged role.

---

### Recommendation

Include `FeeReceiver.balance` directly in `getETHDistributionData()`, or call `sendFunds()` atomically inside `_updateRsETHPrice()` before computing TVL. The simplest fix is to read the reward receiver's balance from the config and add it to `ethLyingInDepositPool`:

```solidity
address rewardReceiver = lrtConfig.getContract(LRTConstants.LRT_REWARD_RECEIVER);
ethLyingInDepositPool = address(this).balance + rewardReceiver.balance;
```

This eliminates the timing dependency entirely and makes the oracle invariant hold regardless of when `sendFunds()` is called.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Fork test — run against a local Anvil fork
// Demonstrates rsETH price differs before/after sendFunds()

function test_blockStuffing_rsETHMispricing() public {
    // 1. Simulate MEV rewards accumulating in FeeReceiver
    uint256 mevRewards = 10 ether;
    vm.deal(address(feeReceiver), mevRewards);

    // 2. Record price WITHOUT calling sendFunds() first
    //    (simulates attacker stuffing blocks to delay sendFunds)
    lrtOracle.updateRSETHPrice();
    uint256 priceWithoutRewards = lrtOracle.rsETHPrice();

    // 3. Now call sendFunds() and update price again
    feeReceiver.sendFunds();
    lrtOracle.updateRSETHPrice();
    uint256 priceWithRewards = lrtOracle.rsETHPrice();

    // 4. Assert price difference equals mevRewards / totalSupply (1e18 precision)
    uint256 rsethSupply = rseth.totalSupply();
    uint256 expectedDelta = (mevRewards * 1e18) / rsethSupply;

    assertApproxEqAbs(
        priceWithRewards - priceWithoutRewards,
        expectedDelta,
        1e9, // tolerance for fee rounding
        "rsETH price must reflect pending MEV rewards"
    );
}
```

### Citations

**File:** contracts/FeeReceiver.sol (L53-58)
```text
    function sendFunds() external {
        uint256 balance = address(this).balance;
        ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();

        emit MevRewardsAddedToTVL(balance);
    }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L249-251)
```text
        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

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

**File:** contracts/LRTDepositPool.sol (L464-467)
```text
    /// @dev provides ETH amount distribution data among depositPool, NDCs and eigenLayer
    /// @dev rewards are not accounted here
    /// it will automatically be accounted once it is moved from feeReceiver/rewardReceiver to depositPool
    function getETHDistributionData()
```

**File:** contracts/LRTDepositPool.sol (L479-500)
```text
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
