### Title
Depositors Can Front-Run Stale `rsETHPrice` to Steal Accumulated Yield from Existing rsETH Holders - (File: `contracts/LRTOracle.sol`, `contracts/LRTDepositPool.sol`)

---

### Summary

`LRTOracle.updateRSETHPrice()` is a permissionless public function that updates the stored `rsETHPrice` based on current underlying asset values. Because deposits in `LRTDepositPool` mint rsETH using the stored (potentially stale) `rsETHPrice`, an attacker can deposit at a below-true-value price immediately before a price update, capturing a disproportionate share of accumulated yield that rightfully belongs to existing long-term rsETH holders.

---

### Finding Description

`LRTOracle._updateRsETHPrice()` computes the rsETH/ETH exchange rate as:

```
newRsETHPrice = (totalETHInProtocol - protocolFeeInETH) / rsethSupply
``` [1](#0-0) 

This stored `rsETHPrice` is only updated when `updateRSETHPrice()` is explicitly called. Between calls, the price is stale. Since underlying assets like stETH rebase daily and other LSTs appreciate continuously, `rsETHPrice` will routinely lag behind the true protocol value.

`updateRSETHPrice()` is public and permissionless: [2](#0-1) 

Deposits in `LRTDepositPool` mint rsETH using the stale stored price:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [3](#0-2) 

There is no call to `updateRSETHPrice()` inside `depositETH` or `depositAsset` before minting: [4](#0-3) 

The attack flow is:

1. Underlying assets (e.g., stETH) appreciate since the last `updateRSETHPrice()` call. The stored `rsETHPrice` is now lower than the true value.
2. Attacker deposits a large amount at the stale (lower) `rsETHPrice`, receiving more rsETH than the true fair value.
3. Attacker (or anyone) calls `updateRSETHPrice()`. The price increases to reflect the accumulated appreciation.
4. Attacker's rsETH is now worth more than deposited. The gain comes directly from diluting existing holders' share of the accumulated yield.

**Concrete example:**
- Protocol holds 100 ETH, 100 rsETH outstanding, `rsETHPrice = 1.00 ETH` (stale).
- True value after stETH rebase: 101 ETH. True rsETH price = 1.01 ETH.
- Attacker deposits 100 ETH at stale price → mints `100 / 1.00 = 100 rsETH`.
- `updateRSETHPrice()` is called: new price = `201 ETH / 200 rsETH = 1.005 ETH`.
- Attacker's 100 rsETH is worth 100.5 ETH — a 0.5 ETH gain.
- Original holders' 100 rsETH is worth 100.5 ETH instead of 101 ETH — they lost 0.5 ETH of yield to the attacker.

The `pricePercentageLimit` guard only blocks updates where the price increase exceeds the configured threshold: [5](#0-4) 

For normal daily stETH rebase (~0.01%/day), the increase is well within any reasonable limit, so the attacker can freely call `updateRSETHPrice()` themselves after depositing.

---

### Impact Explanation

**High — Theft of unclaimed yield.**

Existing rsETH holders accumulate yield as underlying assets appreciate between oracle updates. An attacker who deposits at the stale price before the update captures a portion of that accumulated yield. The attacker profits at the direct expense of long-term depositors. The attack is repeatable every oracle update cycle (daily for stETH rebases), making the cumulative loss significant.

---

### Likelihood Explanation

**High.** stETH rebases every ~24 hours, creating a predictable and recurring window where `rsETHPrice` is stale. The attack requires no special permissions — `stake()` and `updateRSETHPrice()` are both permissionless. An MEV bot can monitor the mempool for oracle update transactions and front-run them, or simply monitor the stETH rebase schedule on-chain. No oracle compromise or admin collusion is required. [2](#0-1) [6](#0-5) 

---

### Recommendation

Call `_updateRsETHPrice()` (or `updateRSETHPrice()`) atomically at the start of `depositETH` and `depositAsset` before computing `rsethAmountToMint`. This ensures every deposit uses the freshest possible price, eliminating the stale-price deposit window. Alternatively, introduce a deposit fee or a time-weighted average price (TWAP) for the rsETH rate to make the attack economically unattractive.

---

### Proof of Concept

```solidity
// Attacker contract
function attack(LRTDepositPool pool, LRTOracle oracle, IERC20 stETH) external payable {
    // Step 1: stETH has rebased since last oracle update — rsETHPrice is stale (low)
    uint256 stalePriceRsETH = oracle.rsETHPrice(); // e.g., 1.00e18

    // Step 2: Deposit at stale price — receive excess rsETH
    stETH.approve(address(pool), type(uint256).max);
    pool.depositAsset(address(stETH), 100_000e18, 0, "attack");
    // Minted: 100_000e18 * assetPrice / stalePriceRsETH > fair share

    // Step 3: Trigger price update — rsETHPrice increases to reflect accumulated yield
    oracle.updateRSETHPrice();
    uint256 newPriceRsETH = oracle.rsETHPrice(); // e.g., 1.01e18

    // Step 4: Attacker's rsETH balance is now worth more than deposited
    // Profit = (newPriceRsETH - stalePriceRsETH) * rsETHBalance / newPriceRsETH
    // This profit is extracted from existing holders' accumulated yield
}
``` [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L214-250)
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

        // calculate previousTVL using rsethSupply multiplied by rsETHPrice
        uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);

        IPausable lrtDepositPool = IPausable(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable withdrawalManager = IPausable(lrtConfig.getContract(LRTConstants.LRT_WITHDRAW_MANAGER));

        // determine if the protocol is active (not paused)
        bool protocolPaused = lrtDepositPool.paused() || withdrawalManager.paused() || paused;

        // only take fee if TVL increased and protocol is not paused
        uint256 protocolFeeInETH = 0;
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L252-266)
```text
        if (newRsETHPrice > highestRsethPrice) {
            // check if the price is above the threshold
            uint256 priceDifference = newRsETHPrice - highestRsethPrice;
            // pricePercentageLimit is in 1e18 precision (100% = 1e18, 1% = 1e16)
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);

            // check if the price difference is above the threshold
            if (isPriceIncreaseOffLimit) {
                // if sender has a manager role, this doesn't revert.
                // if not, it reverts as price went above the threshold
                if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
                    revert PriceAboveDailyThreshold();
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

**File:** contracts/LRTDepositPool.sol (L99-118)
```text
    function depositAsset(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedERC20Token(asset)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);

        emit AssetDeposit(msg.sender, asset, depositAmount, rsethAmountToMint, referralId);
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
