### Title
Inflation Attack via Direct Asset Donation Inflates `rsETHPrice`, Causing Depositors to Receive Zero rsETH - (File: contracts/LRTDepositPool.sol / contracts/LRTOracle.sol)

---

### Summary

`LRTDepositPool.getTotalAssetDeposits()` counts raw on-chain balances (ERC20 `balanceOf` and `address(this).balance`) that any actor can inflate by directly transferring assets to the contract. Because `LRTOracle.updateRSETHPrice()` is an unrestricted public function, an attacker can trigger a price recalculation immediately after donating, permanently inflating the stored `rsETHPrice`. Subsequent depositors who do not set a non-zero `minRSETHAmountExpected` receive zero rsETH in exchange for their deposited assets, which are then claimable by the attacker through their pre-existing rsETH position.

---

### Finding Description

**Step 1 – Attacker seeds a tiny rsETH position.**

`LRTDepositPool.depositETH()` calls `_beforeDeposit()` → `getRsETHAmountToMint()`:

```
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

When `rsETHPrice == 1e18` (the initial value set when `rsethSupply == 0`), depositing `1 wei` of ETH mints `1 wei` of rsETH. [1](#0-0) [2](#0-1) 

**Step 2 – Attacker donates a large amount directly to `LRTDepositPool`.**

For ETH, the contract has an unrestricted `receive()` fallback: [3](#0-2) 

For ERC20 LSTs, `getAssetDistributionData()` counts `IERC20(asset).balanceOf(address(this))` — the raw token balance — which any actor can inflate with a direct `transfer()`: [4](#0-3) 

For ETH, `getETHDistributionData()` counts `address(this).balance`: [5](#0-4) 

**Step 3 – Attacker calls the public `updateRSETHPrice()` to commit the inflated price.**

`updateRSETHPrice()` is `public` with only a `whenNotPaused` guard — no role restriction: [6](#0-5) 

`_updateRsETHPrice()` computes:
```
newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply)
``` [7](#0-6) 

With `rsethSupply == 1 wei` and `totalETHInProtocol ≈ 10 ETH` (the donation), `newRsETHPrice ≈ 10e36`. The price-increase guard is gated on `pricePercentageLimit > 0`, but `pricePercentageLimit` is **never set in `initialize()`**, so it defaults to `0` and the guard is permanently disabled: [8](#0-7) [9](#0-8) 

**Step 4 – Victim deposits; receives zero rsETH.**

With `rsETHPrice ≈ 10e36`, a victim depositing `1 ETH` computes:
```
rsethAmountToMint = (1e18 * 1e18) / 10e36 = 0  (integer division rounds to 0)
```

`_beforeDeposit()` only checks `rsethAmountToMint < minRSETHAmountExpected`. If the victim passes `minRSETHAmountExpected == 0` (the default in many integrations), the deposit succeeds and the victim receives **zero rsETH**: [10](#0-9) 

**Step 5 – Attacker redeems their rsETH, capturing the victim's deposit.**

The attacker holds the only `1 wei` of rsETH. After the victim's ETH is added to the pool, the attacker's rsETH represents 100% of the pool (attacker's original `1 wei` + `10 ETH` donation + victim's `1 ETH`). Upon redemption the attacker recovers all assets, netting the victim's `1 ETH`.

---

### Impact Explanation

**Critical — Direct theft of depositor funds.**

Any depositor who calls `depositETH()` or `depositAsset()` with `minRSETHAmountExpected == 0` (or any value below the rounded-down mint amount) after the attacker has inflated `rsETHPrice` will have their entire deposit absorbed into the pool with no rsETH issued in return. The attacker, holding the only outstanding rsETH, redeems it to claim all pooled assets including the victim's deposit. This is a complete loss of principal for the victim.

---

### Likelihood Explanation

**Medium.**

- `pricePercentageLimit` is `0` by default (not set in `initialize()`), so the price-increase guard is disabled unless the admin explicitly configures it.
- `updateRSETHPrice()` is callable by any EOA or contract with no role restriction.
- `receive()` on `LRTDepositPool` accepts arbitrary ETH; ERC20 tokens can be transferred directly.
- The attack is most effective at protocol launch or after a full withdrawal when `rsethSupply` is very small.
- Victims who omit `minRSETHAmountExpected` (common in scripts and integrations) are fully exposed.
- The attacker must commit capital equal to the donation amount, but recovers it upon redemption; net cost is only gas.

---

### Recommendation

1. **Reject zero-rsETH mints.** Add an explicit check in `_beforeDeposit()`:
   ```solidity
   if (rsethAmountToMint == 0) revert ZeroRsETHMinted();
   ```

2. **Decouple accounting from raw balances.** Track deposited assets in an internal ledger (incremented only through `depositAsset`/`depositETH`) rather than relying on `balanceOf(address(this))` or `address(this).balance`, which are inflatable by direct transfers.

3. **Require `pricePercentageLimit` to be set at initialization.** The current default of `0` disables the only price-spike guard. Enforce a non-zero value in `initialize()`.

4. **Restrict `updateRSETHPrice()`.** Limit callers to a keeper role or the protocol's own deposit/withdrawal flow to prevent arbitrary price manipulation.

---

### Proof of Concept

```
Initial state: rsETHPrice = 1e18, rsethSupply = 0

1. Attacker calls depositETH{value: 1 wei}(0, "")
   → rsethAmountToMint = (1 * 1e18) / 1e18 = 1 wei
   → Attacker holds 1 wei rsETH; pool holds 1 wei ETH

2. Attacker sends 10 ETH directly to LRTDepositPool (via receive())
   → address(LRTDepositPool).balance = 10 ETH + 1 wei

3. Attacker calls LRTOracle.updateRSETHPrice()
   → totalETHInProtocol = 10 ETH + 1 wei
   → newRsETHPrice = (10e18 + 1) * 1e18 / 1 ≈ 10e36
   → pricePercentageLimit == 0 → guard skipped
   → rsETHPrice = 10e36

4. Victim calls depositETH{value: 1 ETH}(0, "")
   → rsethAmountToMint = (1e18 * 1e18) / 10e36 = 0
   → minRSETHAmountExpected = 0 → check passes
   → Victim receives 0 rsETH; 1 ETH added to pool

5. Attacker redeems 1 wei rsETH (only outstanding supply)
   → Receives: 1 wei + 10 ETH + 1 ETH = 11 ETH + 1 wei
   → Net profit: 1 ETH (victim's deposit)
   → Victim loss: 1 ETH (100% of deposit)
```

### Citations

**File:** contracts/LRTDepositPool.sol (L58-58)
```text
    receive() external payable { }
```

**File:** contracts/LRTDepositPool.sol (L444-444)
```text
        assetLyingInDepositPool = IERC20(asset).balanceOf(address(this));
```

**File:** contracts/LRTDepositPool.sol (L480-480)
```text
        ethLyingInDepositPool = address(this).balance;
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

**File:** contracts/LRTDepositPool.sol (L665-669)
```text
        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
```

**File:** contracts/LRTOracle.sol (L64-68)
```text
    function initialize(address lrtConfigAddr) external initializer {
        UtilLib.checkNonZeroAddress(lrtConfigAddr);
        lrtConfig = ILRTConfig(lrtConfigAddr);
        emit UpdatedLRTConfig(lrtConfigAddr);
    }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L218-221)
```text
        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
```

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L256-257)
```text
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
```
