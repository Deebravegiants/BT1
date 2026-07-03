### Title
Wrong rsETH Amount Computation for Non-18 Decimal Tokens in `viewSwapRsETHAmountAndFee` - (`contracts/pools/RSETHPoolV3.sol`, `contracts/pools/RSETHPoolV3ExternalBridge.sol`, `contracts/pools/RSETHPoolV3WithNativeChainBridge.sol`)

---

### Summary

The `viewSwapRsETHAmountAndFee(amount, token)` function in all three V3 pool contracts computes the rsETH amount to mint using `amountAfterFee * tokenToETHRate / rsETHToETHrate`. This formula is correct only when the deposited token has 18 decimals. For tokens with fewer decimals (e.g., wBTC at 8 decimals), the result is orders of magnitude too small, causing depositors to receive nearly zero rsETH in exchange for their full token deposit.

---

### Finding Description

In `RSETHPoolV3.sol`, `RSETHPoolV3ExternalBridge.sol`, and `RSETHPoolV3WithNativeChainBridge.sol`, the ETH deposit path correctly computes:

```solidity
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

Here `amountAfterFee` is in wei (18 decimals) and `rsETHToETHrate` is 1e18-scaled, so the result is correctly in 18-decimal rsETH units.

The token deposit path computes:

```solidity
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

`tokenToETHRate` is fetched from `ChainlinkOracleForRSETHPoolCollateral.getRate()`, which normalizes the Chainlink answer to 1e18 precision — representing the price of **1 whole token** in ETH, scaled to 1e18:

```solidity
uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
return normalizedPrice;
```

So `tokenToETHRate` = (price of 1 whole token in ETH) × 1e18.

For an 18-decimal token (e.g., wstETH), `amountAfterFee` is already in 1e18 units, so the formula cancels correctly. For an 8-decimal token (e.g., wBTC), `amountAfterFee` is in 1e8 units, but `tokenToETHRate` still represents the price of 1 whole wBTC (= 1e8 units). The formula is therefore missing a factor of `1e18 / 10**token.decimals()`.

---

### Impact Explanation

**Critical — Direct theft of user funds.**

A user depositing 1 wBTC (= 1e8 units, worth ~20 ETH) with `rsETHToETHrate = 1.05e18` and `tokenToETHRate = 20e18`:

```
rsETHAmount = 1e8 * 20e18 / 1.05e18
            = 20e8 / 1.05
            ≈ 19.05e8   (≈ 1.905e-10 rsETH)
```

The user should receive `≈ 19.05e18` rsETH (≈ 19.05 rsETH). Instead they receive `≈ 19.05e8` rsETH — a factor of `1e10` less. Their wBTC is transferred into the pool, but the corresponding rsETH is never minted. The unaccounted value accrues to all existing rsETH holders, constituting a direct transfer of depositor funds to existing holders.

For tokens with more than 18 decimals the formula over-mints rsETH, causing protocol insolvency.

---

### Likelihood Explanation

**Medium.** The `supportedTokenOracle` mapping accepts any token address set by an admin. No on-chain constraint enforces 18 decimals for supported tokens. The protocol is explicitly designed to be extensible to new collateral types. Any legitimate admin addition of a non-18 decimal token (e.g., wBTC, USDC) immediately activates the bug for every subsequent depositor of that token.

---

### Recommendation

Normalize `amountAfterFee` to 18 decimals before applying the rate ratio, analogous to the fix recommended in H-02:

```solidity
// rate of token in ETH (1e18-scaled, price of 1 whole token)
uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

// Normalize amount to 18 decimals, then convert via rates
uint256 amountIn18 = amountAfterFee * 1e18 / 10 ** IERC20Metadata(token).decimals();
rsETHAmount = amountIn18 * tokenToETHRate / rsETHToETHrate;
```

---

### Proof of Concept

**Root cause — three identical occurrences:**

`RSETHPoolV3.sol` line 334: [1](#0-0) 

`RSETHPoolV3ExternalBridge.sol` line 452: [2](#0-1) 

`RSETHPoolV3WithNativeChainBridge.sol` line 370: [3](#0-2) 

**Oracle normalization (confirms `tokenToETHRate` is price of 1 whole token × 1e18):** [4](#0-3) 

**Correct ETH path (18-decimal baseline):** [5](#0-4) 

**Numeric walkthrough (wBTC, 8 decimals, price = 20 ETH, rsETH rate = 1.05 ETH):**

| Variable | Value |
|---|---|
| `amountAfterFee` | `1e8` (1 wBTC) |
| `tokenToETHRate` | `20e18` |
| `rsETHToETHrate` | `1.05e18` |
| Actual result | `≈ 19.05e8` rsETH |
| Expected result | `≈ 19.05e18` rsETH |
| Error factor | `1e10` (user receives 10,000,000,000× less) |

The attacker-controlled entry path is the public `deposit(address token, uint256 amount, string referralId)` function, callable by any user. No privilege is required. The depositor's tokens are transferred in full; the minted rsETH is negligible.

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L299-307)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolV3.sol (L330-334)
```text
        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L448-452)
```text
        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L366-370)
```text
        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L34-36)
```text
        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());

        return normalizedPrice;
```
