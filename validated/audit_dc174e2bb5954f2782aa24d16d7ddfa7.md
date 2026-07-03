Audit Report

## Title
Spot `pricePerShare()` Oracle Enables frxETH Donation to Inflate Protocol Fee and Steal Unclaimed Yield — (`contracts/oracles/SfrxETHPriceOracle.sol`, `contracts/LRTOracle.sol`)

## Summary

`SfrxETHPriceOracle.getAssetPrice()` returns sfrxETH's `pricePerShare()` as a raw spot value with no TWAP or manipulation guard. Because sfrxETH is an ERC4626 vault, a direct frxETH transfer to the vault inflates `pricePerShare()` in the same transaction. Since `LRTOracle.updateRSETHPrice()` is a public, permissionless function that uses this spot price to compute `rewardAmount` and mint protocol-fee rsETH to the treasury, an attacker can inflate the fee rsETH minted to the treasury, diluting all existing rsETH holders' unclaimed yield.

## Finding Description

**Unguarded spot oracle.** `SfrxETHPriceOracle.getAssetPrice()` delegates entirely to `pricePerShare()` with no secondary source, TWAP, or deviation check: [1](#0-0) 

sfrxETH's `pricePerShare()` equals `totalAssets() / totalSupply()`. A direct ERC20 transfer of frxETH to the sfrxETH contract increases `totalAssets()` without minting new shares, immediately inflating `pricePerShare()` in the same block.

**Permissionless `updateRSETHPrice()`.** Any EOA can call this function: [2](#0-1) 

**Fee computation uses the manipulable spot price.** Inside `_updateRsETHPrice()`, `_getTotalEthInProtocol()` multiplies the protocol's sfrxETH share balance by the spot `pricePerShare()`. The inflated `totalETHInProtocol` drives an inflated `rewardAmount` and `protocolFeeInETH`: [3](#0-2) 

Excess rsETH is then minted to the treasury: [4](#0-3) 

**`pricePercentageLimit` guard is bypassable.** When `pricePercentageLimit == 0`, the entire check is skipped: [5](#0-4) 

Even when non-zero, the attacker can calibrate the donation to keep the rsETH price increase within the allowed band, since the fee is deducted before computing the new rsETH price, making the rsETH price rise smaller than the raw TVL inflation.

**`maxFeeMintAmountPerDay` caps but does not prevent the attack.** The daily limit reverts if exceeded, but the attacker can still consume the entire daily allowance in a single call, or repeat the attack each day: [6](#0-5) 

**`getTotalAssetDeposits` counts all sfrxETH shares across the protocol**, amplifying the impact of the price inflation: [7](#0-6) 

## Impact Explanation

Every excess rsETH minted to the treasury as protocol fee dilutes the rsETH/ETH exchange rate for all existing holders. Yield that should have accrued to rsETH holders is instead captured by the treasury as an over-stated fee. This is a direct, quantifiable theft of unclaimed yield proportional to the donation size and the protocol's total sfrxETH holdings. This matches the **High — Theft of unclaimed yield** impact class.

## Likelihood Explanation

- sfrxETH is a listed supported asset with non-zero protocol balance.
- `updateRSETHPrice()` requires no role — any EOA can call it.
- frxETH is freely purchasable on-chain; the attacker only needs enough to move `pricePerShare()` by a meaningful amount.
- The attack is atomic (deposit → donate → call oracle → redeem) and requires no privileged access.
- If `pricePercentageLimit == 0`, there is no on-chain revert path for an unprivileged caller.
- The attacker recovers most of the donated frxETH by redeeming their sfrxETH shares; the net cost is only the fraction of the donation that accrues to other sfrxETH holders.

## Recommendation

1. **Replace the spot oracle with a manipulation-resistant price source.** Use a Chainlink frxETH/ETH feed or a TWAP-based oracle instead of reading `pricePerShare()` directly.
2. **If `pricePerShare()` must be used**, enforce a maximum per-update price increase relative to the last recorded value (e.g., cap the sfrxETH price used in fee computation at `lastRecordedPricePerShare * (1 + maxDailyYield)`).
3. **Ensure `pricePercentageLimit` is always non-zero** in production so that large single-block price jumps revert for unprivileged callers.
4. **Consider restricting `updateRSETHPrice()` to a keeper/manager role** or adding a cooldown between successive calls.

## Proof of Concept

Foundry fork test against mainnet:

1. Fork mainnet with sfrxETH as a supported asset with non-zero protocol balance and `maxFeeMintAmountPerDay > 0`.
2. Deploy `DonationAttackPoC` with the LRTOracle, rsETH, and treasury addresses.
3. Fund the attacker with `donationAmount` frxETH.
4. Call `attack(donationAmount)`:
   - Deposit `donationAmount / 2` frxETH into sfrxETH to acquire shares.
   - Record `treasuryBefore = rsETH.balanceOf(treasury)` and `supplyBefore = rsETH.totalSupply()`.
   - Transfer `donationAmount / 2` frxETH directly to the sfrxETH contract, inflating `pricePerShare()`.
   - Call `lrtOracle.updateRSETHPrice()`.
   - Assert `rsETH.balanceOf(treasury) - treasuryBefore > 0` (excess fee minted).
   - Redeem sfrxETH shares to recover most frxETH.
5. Assert that `excessFee > protocolFeeInBPS / 10_000 * genuine_yield_since_last_update`, confirming the fee invariant is broken and yield has been stolen from existing rsETH holders.

### Citations

**File:** contracts/oracles/SfrxETHPriceOracle.sol (L35-41)
```text
    function getAssetPrice(address asset) external view returns (uint256) {
        if (asset != sfrxETHContractAddress) {
            revert InvalidAsset();
        }

        return ISfrxETH(sfrxETHContractAddress).pricePerShare();
    }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L205-209)
```text
        if (currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay) {
            revert DailyFeeMintLimitExceeded(currentPeriodMintedFeeAmount + feeAmount, maxFeeMintAmountPerDay);
        }

        currentPeriodMintedFeeAmount += feeAmount;
```

**File:** contracts/LRTOracle.sol (L231-246)
```text
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
```

**File:** contracts/LRTOracle.sol (L256-257)
```text
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
```

**File:** contracts/LRTOracle.sol (L299-308)
```text
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
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
