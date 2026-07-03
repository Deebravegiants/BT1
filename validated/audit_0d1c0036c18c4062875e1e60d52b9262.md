### Title
Stale Cross-Chain Oracle Rate Enables Structural Over-Minting of wrsETH, Causing Undercollateralization of the L2 Wrapper - (File: contracts/pools/RSETHPoolV3ExternalBridge.sol, contracts/pools/RSETHPoolV3.sol)

---

### Summary

The L2 pool contracts (`RSETHPoolV3`, `RSETHPoolV3ExternalBridge`) mint wrsETH based on a cross-chain oracle rate that can be stale. Because the rsETH price on L1 increases monotonically with staking rewards, and the L2 oracle is only updated when a LayerZero message arrives, the L2 rate will always lag the actual L1 rate between updates. When the L2 rate is stale (lower than actual), every deposit mints more wrsETH than the deposited ETH will produce in rsETH when bridged to L1. This creates a structural, accumulating deficit in the wrsETH wrapper — the direct analog to the Salty.IO undercollateralization finding.

---

### Finding Description

**Step 1 — Minting on L2 uses the stale oracle rate.**

In `RSETHPoolV3.deposit()` and `RSETHPoolV3ExternalBridge.deposit()`, the amount of wrsETH minted is:

```
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate_L2
```

where `rsETHToETHrate_L2` is fetched from `getRate()` → `IOracle(rsETHOracle).getRate()`. [1](#0-0) [2](#0-1) 

There is no staleness check anywhere in this path. The oracle simply returns whatever rate was last received from L1. [3](#0-2) 

**Step 2 — The L2 oracle rate is a cross-chain relay of the L1 price.**

`RSETHRateProvider.getLatestRate()` reads `ILRTOracle(rsETHPriceOracle).rsETHPrice()` — the stored L1 price — and propagates it to L2 via LayerZero. [4](#0-3) 

The L2 receiver (`RSETHRateReceiver`) stores this value and returns it on demand. Between LayerZero message deliveries, the stored rate is frozen at the last received value. [5](#0-4) 

**Step 3 — The L1 rsETH price increases monotonically.**

`LRTOracle._updateRsETHPrice()` computes `newRsETHPrice = totalETHInProtocol / rsethSupply`. As EigenLayer staking rewards accumulate, `totalETHInProtocol` grows while `rsethSupply` stays constant, so `rsETHPrice` only ever increases. [6](#0-5) 

**Step 4 — The L1 vault converts ETH to rsETH at the current (higher) L1 rate.**

When the BRIDGER bridges ETH to L1, `L1VaultV2.depositETHForL1VaultETH()` calls `lrtDepositPool.getRsETHAmountToMint()`:

```
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice()
``` [7](#0-6) [8](#0-7) 

**Step 5 — The mismatch.**

| Quantity | Formula | Value (example) |
|---|---|---|
| wrsETH minted on L2 | `1 ETH * 1e18 / 1.00e18` | **1.000 wrsETH** |
| rsETH received from L1 | `1 ETH * 1e18 / 1.05e18` | **0.952 rsETH** |
| Structural deficit | | **0.048 rsETH per ETH** |

Every deposit during a staleness window creates a deficit. There is no autonomous mechanism to detect or correct this imbalance — the exact structural gap identified in the external report.

---

### Impact Explanation

**High — Theft of unclaimed yield.**

The excess wrsETH minted on L2 represents staking yield that belongs to existing rsETH/wrsETH holders. Each stale-rate deposit dilutes the backing ratio of the wrsETH wrapper. When users later unwrap wrsETH to rsETH, the wrapper is short on rsETH, meaning either some redemptions fail (temporary freeze) or all holders receive less than 1:1 (yield theft). The deficit is proportional to `(rsETHPrice_L1 - rsETHPrice_L2) / rsETHPrice_L2` multiplied by total ETH deposited during the staleness window.

---

### Likelihood Explanation

**Medium.**

The rsETH price grows at roughly the staking APR (~4–5% per year). A 24-hour oracle staleness produces ~0.012% over-minting per deposit; a 7-day staleness produces ~0.087%. LayerZero message delivery is not guaranteed to be instantaneous — network congestion, gas spikes, or infrequent rate-provider calls all cause staleness. No on-chain staleness guard exists in any pool contract or oracle interface, so this condition is reachable by any depositor without any privileged action.

---

### Recommendation

1. Add a `lastUpdatedAt` timestamp to the L2 oracle and revert in `getRate()` if `block.timestamp - lastUpdatedAt > MAX_STALENESS` (e.g., 24 hours).
2. Alternatively, add a staleness check directly in `viewSwapRsETHAmountAndFee()` before using the rate.
3. Implement a circuit breaker that pauses deposits when the oracle rate has not been refreshed within the staleness window.

---

### Proof of Concept

```
Assumptions:
  L1 rsETHPrice (actual)  = 1.05e18  (after 1 week of staking rewards)
  L2 oracle rate (stale)  = 1.00e18  (last updated 1 week ago)
  User deposits 100 ETH, feeBps = 0

On L2 (RSETHPoolV3.deposit):
  rsETHAmount = 100e18 * 1e18 / 1.00e18 = 100.000 wrsETH  ← minted to user

BRIDGER bridges 100 ETH to L1 (L1VaultV2.depositETHForL1VaultETH):
  rsETHAmountToMint = 100e18 * 1e18 / 1.05e18 ≈ 95.238 rsETH  ← bridged back to wrapper

Deficit per cycle: 100.000 - 95.238 = 4.762 rsETH
At scale (10,000 ETH/week deposited during staleness): ~476 rsETH deficit per week
```

The entry path is fully unprivileged: any user calling `deposit()` on `RSETHPoolV3` or `RSETHPoolV3ExternalBridge` during a staleness window triggers the over-minting. No admin action, oracle compromise, or governance capture is required. [9](#0-8) [10](#0-9)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L234-237)
```text
    /// @dev Gets the rate from the rsETHOracle
    function getRate() public view returns (uint256) {
        return IOracle(rsETHOracle).getRate();
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L246-265)
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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L366-384)
```text
    function deposit(string memory referralId)
        external
        payable
        nonReentrant
        whenNotPaused
        limitDailyMint(msg.value, ETH_IDENTIFIER)
    {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L418-427)
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

**File:** contracts/cross-chain/RSETHRateProvider.sol (L27-29)
```text
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
    }
```

**File:** contracts/cross-chain/RSETHRateReceiver.sol (L9-15)
```text
contract RSETHRateReceiver is CrossChainRateReceiver {
    constructor(uint16 _srcChainId, address _rateProvider, address _layerZeroEndpoint) {
        rateInfo = RateInfo({ tokenSymbol: "rsETH", baseTokenSymbol: "ETH" });
        srcChainId = _srcChainId;
        rateProvider = _rateProvider;
        layerZeroEndpoint = _layerZeroEndpoint;
    }
```

**File:** contracts/LRTOracle.sol (L249-251)
```text
        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/L1VaultV2.sol (L224-234)
```text
    function depositETHForL1VaultETH() external payable nonReentrant onlyRole(MANAGER_ROLE) {
        uint256 balanceOfETH = address(this).balance;
        uint256 rsETHAmountToMint = lrtDepositPool.getRsETHAmountToMint(ETH_IDENTIFIER, balanceOfETH);

        if (rsETHAmountToMint == 0) {
            revert InvalidMinRSETHAmountExpected();
        }

        lrtDepositPool.depositETH{ value: balanceOfETH }(rsETHAmountToMint, "");

        emit ETHDepositForL1Vault(balanceOfETH, rsETHAmountToMint);
```
