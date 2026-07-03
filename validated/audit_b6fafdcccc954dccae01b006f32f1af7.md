### Title
Stale rsETH/ETH Rate in `CrossChainRateReceiver` Allows Depositors to Mint Excess rsETH on L2 — (`contracts/cross-chain/CrossChainRateReceiver.sol`)

---

### Summary

The `CrossChainRateReceiver` stores the rsETH/ETH exchange rate received via LayerZero from L1, but `getRate()` returns the stored value with **no staleness check**. All L2 pool variants (`RSETHPoolV3`, `RSETHPoolV2`, `RSETHPoolV2ExternalBridge`, `RSETHPoolV2NBA`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`) use this rate directly to compute how many rsETH/wrsETH tokens to mint per deposited ETH or LST. A depositor can deliberately deposit when the on-chain rate is stale (lower than the true current L1 rate) to receive more rsETH than they are entitled to, diluting existing holders.

---

### Finding Description

`CrossChainRateReceiver` records both the rate and the time it was last updated: [1](#0-0) 

```solidity
uint256 public rate;
uint256 public lastUpdated;
```

The `lzReceive` callback sets both fields when a LayerZero message arrives from the L1 rate provider: [2](#0-1) 

However, `getRate()` simply returns the stored value without consulting `lastUpdated`: [3](#0-2) 

Every L2 pool calls this function at deposit time. For example, `RSETHPoolV3.getRate()`: [4](#0-3) 

The minted rsETH amount is computed as:

```
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate
``` [5](#0-4) 

A lower (stale) `rsETHToETHrate` produces a **larger** `rsETHAmount` for the same deposit. The rate provider (`CrossChainRateProvider.updateRate()` / `MultiChainRateProvider.updateRate()`) is permissionless — anyone can push the latest L1 price to L2 — but there is no requirement to do so before a deposit executes. [6](#0-5) 

The analog to the Flatmoney keeper passing an empty `priceUpdateData` array is a depositor simply **not calling `updateRate()`** before depositing, exploiting the gap between the stale on-chain rate and the true current L1 rate.

---

### Impact Explanation

If the rsETH/ETH rate on L1 has risen (e.g., from 1.00 to 1.05 ETH per rsETH due to staking rewards) but the L2 receiver still holds the old rate of 1.00, a depositor of 1 ETH receives 1 rsETH instead of the correct ~0.952 rsETH. The excess rsETH (~0.048 rsETH) represents value extracted from existing holders, whose proportional claim on the underlying ETH is diluted. This is **theft of unclaimed yield** from existing rsETH/wrsETH holders.

---

### Likelihood Explanation

- The rate update is permissionless but not atomic with deposits; any window between L1 reward accrual and the next LayerZero message is exploitable.
- LayerZero message delivery is not instantaneous and can be delayed by network conditions or simply by no one calling `updateRate()`.
- The attacker needs no special role — any depositor can observe the L1 oracle price, compare it to the stale L2 rate, and deposit opportunistically.

---

### Recommendation

Add a configurable `maxAge` parameter and enforce it inside `getRate()`:

```solidity
uint256 public maxAge; // e.g. 24 hours

function getRate() external view returns (uint256) {
    require(block.timestamp - lastUpdated <= maxAge, "Rate is stale");
    return rate;
}
```

This mirrors the `maxAge` / `maxDiffPercent` pattern used in the Flatmoney fix and ensures that deposits revert when the cross-chain rate has not been refreshed within an acceptable window.

---

### Proof of Concept

1. At T=0, L1 rsETH price = 1.00 ETH. LayerZero pushes this to L2; `CrossChainRateReceiver.rate = 1e18`.
2. At T=1 day, staking rewards accrue on L1; rsETH price rises to 1.05 ETH. No one calls `updateRate()`.
3. Attacker deposits 1 ETH into `RSETHPoolV3.deposit()` on L2.
4. `getRate()` returns the stale `1e18`; attacker receives `1e18 * 1e18 / 1e18 = 1e18` wrsETH (1 wrsETH).
5. Attacker (or anyone) calls `CrossChainRateProvider.updateRate()`; L2 rate updates to `1.05e18`.
6. Attacker's 1 wrsETH is now redeemable for 1.05 ETH worth of assets, having paid only 1 ETH — a 5% gain extracted from existing holders. [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L13-16)
```text
    uint256 public rate;

    /// @notice Last time rate was updated
    uint256 public lastUpdated;
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L82-105)
```text
    function lzReceive(uint16 _srcChainId, bytes memory _srcAddress, uint64, bytes calldata _payload) external {
        require(msg.sender == layerZeroEndpoint, "Sender should be lz endpoint");

        address srcAddress;
        assembly {
            srcAddress := mload(add(_srcAddress, 20))
        }

        require(_srcChainId == srcChainId, "Src chainId must be correct");
        require(srcAddress == rateProvider, "Src address must be provider");

        uint256 _rate = abi.decode(_payload, (uint256));

        rate = _rate;

        lastUpdated = block.timestamp;

        emit RateUpdated(_rate);
    }

    /// @notice Gets the last stored rate in the contract
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L234-237)
```text
    /// @dev Gets the rate from the rsETHOracle
    function getRate() public view returns (uint256) {
        return IOracle(rsETHOracle).getRate();
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L246-264)
```text
    function deposit(string memory referralId)
        external
        payable
        nonReentrant
        whenNotPaused
        limitDailyMint(msg.value, ETH_IDENTIFIER)
    {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
```

**File:** contracts/cross-chain/CrossChainRateProvider.sol (L85-101)
```text
    function updateRate() external payable nonReentrant {
        uint256 latestRate = getLatestRate();

        bytes memory remoteAndLocalAddresses = abi.encodePacked(rateReceiver, address(this));

        rate = latestRate;

        lastUpdated = block.timestamp;

        bytes memory _payload = abi.encode(latestRate);

        ILayerZeroEndpoint(layerZeroEndpoint).send{ value: msg.value }(
            dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
        );

        emit RateUpdated(rate);
    }
```
