### Title
Stale Cached `rsETHPrice` Used in Deposit Minting Calculations Without Prior Refresh - (File: `contracts/LRTDepositPool.sol`)

### Summary
`LRTDepositPool.getRsETHAmountToMint()` divides by `LRTOracle.rsETHPrice`, a cached state variable that is only updated when `updateRSETHPrice()` is explicitly called. Because no deposit path forces a price refresh before minting, a depositor can exploit a stale (lower-than-real) cached price to receive more rsETH than the protocol intends, diluting existing holders' accrued yield.

### Finding Description

`LRTOracle` stores the rsETH/ETH exchange rate as a plain state variable: [1](#0-0) 

It is only updated when `_updateRsETHPrice()` is invoked, either via the public `updateRSETHPrice()` or the manager-gated `updateRSETHPriceAsManager()`: [2](#0-1) 

`LRTDepositPool.getRsETHAmountToMint()` consumes this cached value directly, with no prior call to refresh it: [3](#0-2) 

The same cached value flows into every user-facing deposit entry point through `_beforeDeposit`: [4](#0-3) 

Because rsETH accrues staking rewards continuously, its real price rises monotonically over time. Whenever `updateRSETHPrice()` has not been called recently, `rsETHPrice` lags behind the true value. The minting formula

```
rsethAmountToMint = (amount × assetPrice) / rsETHPrice
```

produces a larger-than-correct rsETH amount when `rsETHPrice` is depressed relative to reality.

The same structural flaw exists in the L2 pool layer. `CrossChainRateReceiver` stores a cached rate that is only refreshed when a LayerZero message arrives: [5](#0-4) [6](#0-5) 

L2 pools (`RSETHPoolV3`, `RSETHPoolV2ExternalBridge`, `RSETHPoolNoWrapper`) call `getRate()` on this receiver without any staleness guard: [7](#0-6) [8](#0-7) 

The `RSETHMultiChainRateProvider` itself reads the already-cached L1 price rather than computing a fresh value: [9](#0-8) 

So the L2 rate is doubly stale: it reflects the last time `updateRSETHPrice()` was called on L1 **and** the last time a LayerZero message was delivered to L2.

### Impact Explanation

When `rsETHPrice` is stale (lower than the real price), every depositor receives excess rsETH proportional to the price gap. This excess is not backed by any additional ETH in the protocol, so it directly dilutes the yield that existing rsETH holders have accrued since the last price update. The stolen quantity per deposit is:

```
excess_rsETH ≈ amount × (1/P_cached − 1/P_real)
```

where `P_real > P_cached`. This constitutes **theft of unclaimed yield** from existing holders (High impact).

### Likelihood Explanation

`updateRSETHPrice()` is a public function with no access restriction, so any actor can call it. In practice the protocol relies on an off-chain keeper. During any keeper outage, network congestion, or deliberate omission, the price drifts. On L2 the staleness window is compounded by the cross-chain message round-trip. A sophisticated depositor can passively monitor `LRTOracle.rsETHPrice` vs. the real TVL-derived price and time deposits to maximise the gap. Likelihood is **Medium**.

### Recommendation

1. In `LRTDepositPool.depositETH()` and `depositAsset()`, call `ILRTOracle(lrtOracleAddress).updateRSETHPrice()` before invoking `_beforeDeposit()`, ensuring the price is always fresh at the point of minting.
2. In L2 pools, add a `lastUpdated` staleness check inside `getRate()` (e.g., revert if `block.timestamp − lastUpdated > MAX_STALENESS`) so deposits revert rather than proceed with a stale rate.
3. Consider making `getRsETHAmountToMint` call an internal view that computes the price on-the-fly from current TVL, removing reliance on the cached state variable entirely.

### Proof of Concept

1. At time `T`, `updateRSETHPrice()` is called; `rsETHPrice = 1.05 ETH` (reflecting accrued rewards).
2. 24 hours pass; staking rewards push the real rsETH price to `1.06 ETH`. The keeper bot is delayed; `rsETHPrice` remains `1.05 ETH`.
3. Attacker calls `LRTDepositPool.depositETH{value: 100 ETH}(0, "")`.
4. `getRsETHAmountToMint` computes `100e18 / 1.05e18 ≈ 95.238 rsETH` instead of the correct `100e18 / 1.06e18 ≈ 94.340 rsETH`.
5. Attacker receives **~0.898 rsETH excess** (~$2,700 at $3,000/ETH) at the expense of existing holders.
6. Attacker immediately calls `updateRSETHPrice()` to lock in the dilution before the next legitimate update. [10](#0-9) [2](#0-1) [11](#0-10)

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

**File:** contracts/LRTDepositPool.sol (L516-521)
```text
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
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

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L13-14)
```text
    uint256 public rate;

```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L93-97)
```text
        uint256 _rate = abi.decode(_payload, (uint256));

        rate = _rate;

        lastUpdated = block.timestamp;
```

**File:** contracts/pools/RSETHPoolV3.sol (L235-237)
```text
    function getRate() public view returns (uint256) {
        return IOracle(rsETHOracle).getRate();
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L299-308)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
    }
```

**File:** contracts/cross-chain/RSETHMultiChainRateProvider.sol (L26-28)
```text
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
    }
```
