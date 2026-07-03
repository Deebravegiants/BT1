### Title
Stale `rsETHPrice` Used in `LRTDepositPool.getRsETHAmountToMint()` Without Prior Update Enables Theft of Unclaimed Yield — (File: contracts/LRTDepositPool.sol)

---

### Summary

`LRTDepositPool.getRsETHAmountToMint()` divides by `lrtOracle.rsETHPrice()`, a **stored/cached value** that must be explicitly refreshed via a separate `updateRSETHPrice()` call. When staking rewards accrue and the price has not been updated, the stored price is lower than the true price. A depositor who calls `depositAsset()` at that moment receives more rsETH than the current protocol value warrants, diluting existing holders and extracting their unclaimed yield.

---

### Finding Description

`LRTOracle` stores `rsETHPrice` as a persistent state variable: [1](#0-0) 

The price is only updated when `_updateRsETHPrice()` is explicitly invoked. A public entry-point exists for this (the presence of `updateRSETHPriceAsManager()` whose sole stated purpose is to bypass the threshold guard that the public version enforces confirms a public `updateRSETHPrice()` exists): [2](#0-1) 

`LRTDepositPool.getRsETHAmountToMint()` reads the stored price directly, with no prior refresh: [3](#0-2) 

The formula is:

```
rsethAmountToMint = (amount × assetPrice) / rsETHPrice
```

If `rsETHPrice` is stale-low (rewards have accrued but the price has not been updated), the denominator is smaller than it should be, so `rsethAmountToMint` is larger than it should be. The depositor receives excess rsETH that represents yield belonging to existing holders.

The desync scenario mirrors the original report exactly:

| Original (HSG) | LRT-rsETH analog |
|---|---|
| Signers regain eligibility → valid signer count rises | Rewards accrue → true rsETH price rises |
| `reconcileSignerCount()` not called before `checkTransaction()` | `updateRSETHPrice()` not called before `depositAsset()` |
| Stored threshold is lower than actual valid count | Stored `rsETHPrice` is lower than actual price |
| Transactions blocked despite enough valid signers | Depositor mints excess rsETH at the expense of existing holders |

---

### Impact Explanation

**High — Theft of unclaimed yield.**

Every unit of accrued-but-unrecorded yield that a new depositor captures at the stale price is yield that existing rsETH holders earned and will never receive. The magnitude scales with: (a) the size of the deposit, (b) the staleness of `rsETHPrice`, and (c) the total rewards that have accrued since the last update. A sophisticated actor can monitor on-chain reward accrual and time large deposits to maximise extraction.

---

### Likelihood Explanation

**Medium.**

`rsETHPrice` is not updated atomically with every deposit; it requires a separate transaction. Any gap between reward accrual and the next price update creates the window. On a live protocol with continuous EigenLayer rewards, this window exists continuously. The attacker needs only to observe that `lrtOracle.rsETHPrice()` is below the value that `_getTotalEthInProtocol() / rsETH.totalSupply()` would produce, then front-run or simply deposit before the next update.

---

### Recommendation

Call `updateRSETHPrice()` (or its internal equivalent) at the start of `depositAsset()` before invoking `getRsETHAmountToMint()`, analogous to the recommended fix in the original report (calling `reconcileSignerCount()` before the validation code in `checkTransaction()`). This ensures the price used for minting always reflects the current protocol state.

---

### Proof of Concept

1. Protocol TVL is 1 050 ETH; rsETH supply is 1 000; true price = 1.05 ETH/rsETH. `rsETHPrice` was last stored at 1.00 ETH/rsETH (before the latest reward epoch).
2. Attacker calls `LRTDepositPool.depositAsset(stETH, 105e18, ...)`.
3. `getRsETHAmountToMint` computes: `105e18 × 1e18 / 1.00e18 = 105 rsETH`.
4. Correct amount at true price: `105e18 × 1e18 / 1.05e18 ≈ 100 rsETH`.
5. Attacker receives **5 excess rsETH** — the exact yield that the 1 000 existing holders earned during the reward epoch.
6. When `updateRSETHPrice()` is subsequently called, the new price is computed over a supply that is now 1 105 rsETH instead of 1 100, permanently diluting all prior holders. [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
```

**File:** contracts/LRTOracle.sol (L91-96)
```text
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
