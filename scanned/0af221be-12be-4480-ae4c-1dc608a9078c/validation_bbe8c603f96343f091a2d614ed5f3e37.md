### Title
Stale `rsETHPrice` Used in Deposit Mint Calculation Allows Depositors to Capture Accrued Yield - (File: `contracts/LRTDepositPool.sol`)

### Summary
`LRTDepositPool.getRsETHAmountToMint()` reads `lrtOracle.rsETHPrice()`, a stored state variable in `LRTOracle`, without first calling `lrtOracle.updateRSETHPrice()`. As EigenLayer staking rewards accrue between price updates, the stored `rsETHPrice` becomes artificially low relative to the true current rate. Any depositor who deposits during this staleness window receives more rsETH than they are entitled to, capturing yield that belongs to existing rsETH holders.

### Finding Description
`LRTOracle.rsETHPrice` is a stored state variable updated only when `updateRSETHPrice()` is explicitly called. It is not refreshed automatically on read. The deposit calculation in `LRTDepositPool` reads this stored value directly:

```solidity
// contracts/LRTDepositPool.sol:520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

`lrtOracle.rsETHPrice()` returns the last written value of the `rsETHPrice` storage slot in `LRTOracle`:

```solidity
// contracts/LRTOracle.sol:28
uint256 public override rsETHPrice;
```

This value is only updated inside `_updateRsETHPrice()`, which is triggered by `updateRSETHPrice()` (public, `whenNotPaused`) or `updateRSETHPriceAsManager()` (manager-only). Neither is called atomically within the deposit flow.

Over time, EigenLayer staking rewards cause the true TVL to grow. `_getTotalEthInProtocol()` reads live EigenLayer strategy balances, so the true rsETH/ETH rate rises continuously. However, `rsETHPrice` remains at its last stored value until an explicit update call. During this window, `rsETHPrice` is lower than the true current rate.

Because `rsethAmountToMint = (amount * assetPrice) / rsETHPrice`, a lower-than-true `rsETHPrice` denominator causes the depositor to receive more rsETH than their deposit is worth at the true current rate. This excess rsETH represents a dilution of all existing holders' positions — the accrued yield that should have been reflected in the price is instead partially transferred to the new depositor.

The same stale read occurs in `LRTWithdrawalManager.getExpectedAssetAmount()`:

```solidity
// contracts/LRTWithdrawalManager.sol:593
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

and in `_createUnlockParams()`:

```solidity
// contracts/LRTWithdrawalManager.sol:847
rsETHPrice: lrtOracle.rsETHPrice(),
```

The deposit path is the exploitable direction: a stale low price benefits the depositor at the expense of existing holders.

### Impact Explanation
**High — Theft of unclaimed yield.** Existing rsETH holders accumulate yield as EigenLayer rewards increase the protocol TVL. This yield is reflected in a rising rsETH/ETH rate. When a depositor mints rsETH against a stale (lower) rate, they receive a larger share of the total supply than their deposit warrants. When `updateRSETHPrice()` is eventually called, the price increase is smaller than it would have been (because the supply is now larger), meaning existing holders receive less yield than they earned. The magnitude scales with deposit size and the duration of the staleness window.

### Likelihood Explanation
**Medium.** `updateRSETHPrice()` is public but is not called atomically with deposits. There is always a non-zero window between the last price update and any given deposit. The window widens if the `pricePercentageLimit` guard causes the update to revert for non-managers (line 263–265 of `LRTOracle.sol`), or if the keeper bot is delayed. A sophisticated depositor can monitor the on-chain TVL (via `_getTotalEthInProtocol()` inputs) to identify when the stored price is most stale and time a large deposit accordingly.

### Recommendation
Call `lrtOracle.updateRSETHPrice()` at the start of `getRsETHAmountToMint()` before reading `lrtOracle.rsETHPrice()`, or inline the price refresh inside `_beforeDeposit()` in `LRTDepositPool`. This ensures the mint calculation always uses the current exchange rate, mirroring the fix pattern described in the reference report (accruing interest before performing the rate-dependent calculation).

### Proof of Concept
1. EigenLayer staking rewards accrue over several hours, increasing the true protocol TVL. The true rsETH/ETH rate is now `1.002e18`, but `lrtOracle.rsETHPrice` still stores `1.001e18` from the last update.
2. Attacker calls `LRTDepositPool.depositETH{value: 1000 ether}(0, "")`.
3. `_beforeDeposit` → `getRsETHAmountToMint(ETH, 1000e18)` computes:
   `rsethAmountToMint = (1000e18 * 1e18) / 1.001e18 ≈ 999.001 rsETH`
   At the true rate it should be: `(1000e18 * 1e18) / 1.002e18 ≈ 998.004 rsETH`
4. Attacker receives ~0.997 rsETH more than deserved.
5. When `updateRSETHPrice()` is called, the new price is computed over a larger supply, so the price increase is smaller than it would have been — existing holders receive proportionally less yield.
6. The attacker can repeat this on every staleness window, systematically extracting yield from existing holders with no special privileges beyond being a normal depositor. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/LRTDepositPool.sol (L515-521)
```text
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

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

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```

**File:** contracts/LRTWithdrawalManager.sol (L590-594)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L846-848)
```text
        return UnlockParams({
            rsETHPrice: lrtOracle.rsETHPrice(),
            assetPrice: lrtOracle.getAssetPrice(asset),
```
