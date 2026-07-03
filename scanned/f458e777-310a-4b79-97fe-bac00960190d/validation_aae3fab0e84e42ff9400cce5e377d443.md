### Title
Overstated rsETH Price Due to Pre-Mint Supply Used in Fee Conversion — (File: contracts/LRTOracle.sol)

### Summary
`_updateRsETHPrice` computes the new rsETH price using the token supply **before** minting protocol-fee tokens, then stores that pre-mint price as the canonical `rsETHPrice`. Because the denominator is too small, the stored price is systematically higher than the actual post-mint price, causing every subsequent depositor to receive fewer rsETH tokens than they are entitled to.

### Finding Description
Inside `_updateRsETHPrice`, the price and the fee-token quantity are computed in sequence:

```solidity
// contracts/LRTOracle.sol  lines 250-306
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
...
uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);
...
IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
...
rsETHPrice = newRsETHPrice;
``` [1](#0-0) [2](#0-1) 

`newRsETHPrice` is `(E − F) / S`, where `E` = total ETH, `F` = fee in ETH, `S` = current supply. After minting `F / newRsETHPrice = F·S/(E−F)` new tokens, the actual supply becomes `S·E/(E−F)` and the true price is:

```
actualPrice = (E − F) / (S·E/(E−F)) = (E−F)² / (S·E)
```

The stored price `(E−F)/S` exceeds the actual price by a factor of `E/(E−F)`. For every subsequent deposit, `getRsETHAmountToMint` in `LRTDepositPool` divides by the overstated `rsETHPrice`:

```solidity
// contracts/LRTDepositPool.sol  line 520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [3](#0-2) 

Because `rsETHPrice` is too high, `rsethAmountToMint` is too low. A depositor of `d` ETH receives tokens worth only `d·(E−F)/E` ETH — a systematic shortfall of `d·F/E`.

This is the direct analog of the biased-estimator pattern: the formula uses an incorrect denominator (`S` instead of the post-mint `S + feeTokens`), producing a price that is consistently biased upward, just as the original report's formula used `T` instead of `T−1`, producing a volatility that was consistently biased downward.

### Impact Explanation
Every depositor who calls `depositETH` or `depositAsset` after a price update receives fewer rsETH than their ETH entitles them to. The shortfall per deposit is proportional to `F/E` (protocol fee / TVL). The "missing" value accrues to existing rsETH holders, who can redeem at the inflated price. This is a continuous, protocol-wide wealth transfer from new depositors to existing holders. Impact: **Low — contract fails to deliver promised returns**.

### Likelihood Explanation
`updateRSETHPrice` is a public, permissionless function callable by anyone. It is expected to be called regularly (at minimum once per day). Every call that processes non-zero rewards introduces the bias. All subsequent deposits until the next price update are affected. Likelihood: **High** (occurs on every normal reward cycle).

### Recommendation
After minting the fee tokens, recompute and store the post-mint price:

```solidity
// After minting fee tokens, update supply-aware price
uint256 updatedSupply = IRSETH(rsETHTokenAddress).totalSupply(); // includes newly minted fee tokens
rsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(updatedSupply);
```

Alternatively, solve for the fee-token quantity algebraically using the post-mint supply to avoid the circular dependency entirely.

### Proof of Concept
Let `E = 1000 ETH`, `S = 1000 rsETH` (price = 1.0), rewards = 10 ETH, fee = 10% → `F = 1 ETH`.

**Current code:**
- `newRsETHPrice = (1000 − 1) / 1000 = 0.999`
- `feeTokens = 1 / 0.999 ≈ 1.001 rsETH` minted to treasury
- Stored `rsETHPrice = 0.999`
- Actual price = `999 / 1001.001 ≈ 0.998`

**Depositor deposits 10 ETH:**
- Gets `10 / 0.999 ≈ 10.01 rsETH` (using stored price)
- Actual value of those tokens = `10.01 × 0.998 ≈ 9.99 ETH`
- Depositor loses ≈ 0.1% of deposit value

**Correct behavior (post-mint price):**
- Stored price should be `≈ 0.998`
- Depositor gets `10 / 0.998 ≈ 10.02 rsETH`, worth `10.02 × 0.998 ≈ 10 ETH` ✓

### Citations

**File:** contracts/LRTOracle.sol (L250-251)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

```

**File:** contracts/LRTOracle.sol (L299-313)
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
        } else {
            _checkAndUpdateDailyFeeMintLimit(0);
        }

        rsETHPrice = newRsETHPrice;
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```
