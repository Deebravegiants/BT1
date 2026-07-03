Audit Report

## Title
Stale `rsETHPrice` During Price-Increase Circuit-Breaker Window Enables Over-Minting of rsETH — (`contracts/LRTOracle.sol`)

## Summary

When the computed new rsETH price exceeds `highestRsethPrice` by more than `pricePercentageLimit`, `_updateRsETHPrice()` reverts for any non-manager caller, leaving `rsETHPrice` frozen at a below-actual value. Because `updateRSETHPrice()` is a public function and deposits use the stale `rsETHPrice` as the denominator for minting, any depositor can mint excess rsETH during the window between the public revert and a manager's manual intervention via `updateRSETHPriceAsManager()`, extracting value from existing rsETH holders' accrued yield.

## Finding Description

`LRTOracle._updateRsETHPrice()` computes `newRsETHPrice` from on-chain TVL and rsETH supply, then applies a price-increase gate:

```solidity
// contracts/LRTOracle.sol lines 252-266
if (newRsETHPrice > highestRsethPrice) {
    uint256 priceDifference = newRsETHPrice - highestRsethPrice;
    bool isPriceIncreaseOffLimit =
        pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);

    if (isPriceIncreaseOffLimit) {
        if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
            revert PriceAboveDailyThreshold();
        }
    }
}
``` [1](#0-0) 

When this revert fires, execution never reaches the state-writing lines:

```solidity
// contracts/LRTOracle.sol lines 294-313
if (newRsETHPrice > highestRsethPrice) {
    highestRsethPrice = newRsETHPrice;
}
// ...
rsETHPrice = newRsETHPrice;
``` [2](#0-1) 

Both `rsETHPrice` and `highestRsethPrice` remain at their previous stale values. The public entry point has no access restriction:

```solidity
// contracts/LRTOracle.sol line 87
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
``` [3](#0-2) 

The only escape is `updateRSETHPriceAsManager()`, which requires the `MANAGER` role: [4](#0-3) 

The stale `rsETHPrice` is consumed directly in the deposit minting path:

```solidity
// contracts/LRTDepositPool.sol line 520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [5](#0-4) 

A stale-low `rsETHPrice` denominator causes the division to yield a larger `rsethAmountToMint` than the depositor's contribution warrants at the actual price. The withdrawal path is also affected but in the opposite direction (withdrawers receive fewer assets), which does not benefit the attacker.

**Exploit flow:**
1. Staking rewards accumulate; on-chain TVL implies `newRsETHPrice` exceeds `highestRsethPrice` by more than `pricePercentageLimit`.
2. Any caller invokes `updateRSETHPrice()`. The function reverts with `PriceAboveDailyThreshold`. `rsETHPrice` stays stale.
3. Attacker calls `LRTDepositPool.depositAsset()`. `getRsETHAmountToMint()` divides by the stale-low `rsETHPrice`, minting excess rsETH.
4. Manager eventually calls `updateRSETHPriceAsManager()`, updating `rsETHPrice` to the actual higher value.
5. Attacker's excess rsETH is now worth more ETH than deposited, with the surplus extracted from existing holders' accrued yield.

No existing guard prevents this: `minRSETHAmountExpected` in `depositAsset()` is set by the attacker themselves and provides no protection; the deposit pool's `whenNotPaused` check is irrelevant since the oracle is not paused in this scenario. [6](#0-5) 

## Impact Explanation

**High — Theft of unclaimed yield.** The yield accrued by existing rsETH holders (staking rewards reflected in the rising TVL) is partially captured by new depositors who mint at the stale-low price. Each rsETH minted at the stale price represents a claim on more protocol TVL than the depositor contributed. The magnitude per deposit is:

```
excess_rsETH = deposit_ETH_value * (1/stale_price - 1/actual_price)
```

For a 1.54% price gap (stale `1.04e18`, actual `1.056e18`) and a 1,000 ETH deposit, approximately 14.6 rsETH (~15 ETH of value at actual price) is over-minted. Multiple depositors can exploit the window simultaneously, and the window can persist for hours or days depending on manager response time.

## Likelihood Explanation

The trigger condition requires no attacker action to create. It arises naturally when:
- `updateRSETHPrice()` is not called for an extended period (e.e., low-activity periods or keeper downtime), allowing accumulated staking rewards to push the computed price above the threshold in one step.
- A sudden increase in an underlying LST/ETH rate (e.g., after a large Lido reward distribution) raises `totalETHInProtocol` and thus `newRsETHPrice` in a single block.
- `pricePercentageLimit` is set to a small value (e.g., 1%, i.e., `1e16`), which even modest multi-day reward accumulation can exceed.

An attacker only needs to observe that `updateRSETHPrice()` reverts on-chain and then deposit before the manager responds. This is a passive, low-effort exploit requiring no capital beyond the deposit itself.

## Recommendation

1. **Clamp instead of revert**: when `isPriceIncreaseOffLimit` is true for a non-manager caller, update `rsETHPrice` to `highestRsethPrice * (1 + pricePercentageLimit)` (the band boundary) rather than reverting. This ensures the price is always advanced to at least the permitted maximum, eliminating the stale window.
2. **Separate the guard from the price write**: allow the price to be written up to the capped value unconditionally; only gate the full jump (beyond the cap) behind the manager role.
3. **Automated keeper**: ensure an on-chain keeper or Gelato task calls `updateRSETHPriceAsManager()` promptly whenever the public call reverts, minimising the stale window as an operational mitigation.

## Proof of Concept

**Minimal Foundry fork test plan:**

1. Fork mainnet; deploy or use existing `LRTOracle`, `LRTDepositPool`, rsETH.
2. Set `pricePercentageLimit = 1e16` (1%). Record `highestRsethPrice = H`, `rsETHPrice = H`.
3. Warp time forward several days without calling `updateRSETHPrice()`. Simulate reward accrual by increasing the mock LST oracle price so that `_getTotalEthInProtocol()` returns a value implying `newRsETHPrice = H * 1.0154` (1.54% above `H`).
4. Call `updateRSETHPrice()` from an unprivileged EOA. Assert it reverts with `PriceAboveDailyThreshold`. Assert `rsETHPrice == H` (unchanged).
5. From attacker EOA, call `depositAsset(stETH, 1000e18, 0, "")`. Record `rsethMinted`.
6. From manager EOA, call `updateRSETHPriceAsManager()`. Assert `rsETHPrice == H * 1.0154`.
7. Compute `attackerETHValue = rsethMinted * newRsETHPrice / 1e18`. Assert `attackerETHValue > 1000e18`, confirming profit extracted from existing holders.
8. Compute `fairRsETH = 1000e18 * 1e18 / (H * 1.0154)`. Assert `rsethMinted > fairRsETH`, confirming over-mint.

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L94-96)
```text
    function updateRSETHPriceAsManager() external onlyLRTManager {
        _updateRsETHPrice();
    }
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

**File:** contracts/LRTOracle.sol (L293-313)
```text
        // update highest price if new price exceeds it
        if (newRsETHPrice > highestRsethPrice) {
            highestRsethPrice = newRsETHPrice;
        }

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

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```
