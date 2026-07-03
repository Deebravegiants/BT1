### Title
Stale `rsETHPrice` Used in `LRTDepositPool::getRsETHAmountToMint` Allows Depositors to Receive Excess rsETH at the Expense of Existing Holders - (`contracts/LRTDepositPool.sol`)

---

### Summary

`LRTDepositPool.getRsETHAmountToMint()` divides by `lrtOracle.rsETHPrice()`, which is a **cached storage variable** in `LRTOracle` that is only updated when `updateRSETHPrice()` is explicitly called. Deposit functions never call `updateRSETHPrice()` before computing the mint amount. When the protocol has accrued rewards since the last price update, the stale (lower) `rsETHPrice` causes depositors to receive more rsETH than they are entitled to, diluting existing holders' yield.

---

### Finding Description

`LRTOracle` stores the rsETH/ETH exchange rate in a public state variable `rsETHPrice`: [1](#0-0) 

This variable is only updated when `updateRSETHPrice()` (or `updateRSETHPriceAsManager()`) is explicitly called: [2](#0-1) 

When a user calls `depositETH()` or `depositAsset()` on `LRTDepositPool`, the flow is:

`depositETH()` → `_beforeDeposit()` → `getRsETHAmountToMint()`: [3](#0-2) 

The mint amount is computed as `(amount * assetPrice) / lrtOracle.rsETHPrice()`. Neither `depositETH()` nor `depositAsset()` calls `updateRSETHPrice()` before this calculation: [4](#0-3) 

The actual current rsETH price is computed inside `_updateRsETHPrice()` by summing all TVL across NodeDelegators and dividing by total supply: [5](#0-4) 

Between two consecutive calls to `updateRSETHPrice()`, the protocol accumulates staking rewards (ETH staking yield, EigenLayer AVS rewards). The actual rsETH price rises, but `rsETHPrice` in storage remains at the old lower value. Any deposit during this window uses the stale denominator, minting more rsETH than the depositor is entitled to.

Additionally, `RSETHPriceFeed` exposes this same stale value as a Chainlink-compatible feed: [6](#0-5) 

---

### Impact Explanation

When `rsETHPrice` is stale (lower than the true current price because rewards have accrued):

- True price: `1.05 ETH/rsETH` (after rewards)
- Stale stored price: `1.00 ETH/rsETH`
- Depositor sends `1 ETH` and receives `1/1.00 = 1.0 rsETH` instead of the correct `1/1.05 ≈ 0.952 rsETH`

The excess `0.048 rsETH` represents a claim on protocol TVL that was earned by existing holders. The depositor effectively captures a portion of accrued yield that belongs to prior rsETH holders. This is **theft of unclaimed yield** (High severity per the allowed impact scope).

---

### Likelihood Explanation

`updateRSETHPrice()` is called by an off-chain keeper/bot, not atomically with every deposit. The protocol's own `pricePercentageLimit` guard and daily fee minting logic confirm that price updates are periodic, not per-block. Any deposit in the window between reward accrual and the next `updateRSETHPrice()` call exploits this. A sophisticated user can monitor on-chain TVL (via `_getTotalEthInProtocol()`) versus the stored `rsETHPrice` and time deposits to maximize the discrepancy.

---

### Recommendation

Call `_updateRsETHPrice()` (or expose it as an internal call) at the start of `depositETH()` and `depositAsset()` before computing the mint amount, analogous to how the external report recommends updating the underlying pool state before reading prices. Alternatively, compute the rsETH mint amount using a freshly calculated price rather than the cached `rsETHPrice` storage variable.

---

### Proof of Concept

1. Protocol has 1000 ETH TVL, 1000 rsETH supply → `rsETHPrice = 1.0 ETH`.
2. Staking rewards of 10 ETH accrue → true TVL = 1010 ETH, true price = `1.01 ETH/rsETH`.
3. `updateRSETHPrice()` has not yet been called; `rsETHPrice` still = `1.0`.
4. Attacker calls `depositETH{value: 100 ETH}(0, "")`.
5. `getRsETHAmountToMint` computes: `(100e18 * 1e18) / 1e18 = 100 rsETH`.
6. Correct amount at true price: `100e18 / 1.01e18 ≈ 99.01 rsETH`.
7. Attacker receives `~0.99 rsETH` excess, representing ~0.99% of the 10 ETH reward pool stolen from existing holders.
8. After `updateRSETHPrice()` is called, the new price reflects the diluted supply, and existing holders receive less yield than they earned. [7](#0-6) [8](#0-7)

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

**File:** contracts/LRTDepositPool.sol (L506-521)
```text
    function getRsETHAmountToMint(
        address asset,
        uint256 amount
    )
        public
        view
        override
        returns (uint256 rsethAmountToMint)
    {
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/oracles/RSETHPriceFeed.sol (L63-70)
```text
    function latestRoundData()
        external
        view
        returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)
    {
        (roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.latestRoundData();
        answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
    }
```
