### Title
Stale `rsETHPrice` Cache Allows Unprivileged Depositor to Extract Yield by Sandwiching a Public Price Update - (File: contracts/LRTOracle.sol, contracts/LRTDepositPool.sol)

---

### Summary

`LRTOracle.updateRSETHPrice()` is a public, permissionless function. The `rsETHPrice` it maintains is a stale cached value that is only updated on explicit calls. `LRTDepositPool.getRsETHAmountToMint()` uses this stale cached price to determine how many rsETH tokens to mint for a deposit. Because no price refresh is triggered atomically inside the deposit flow, an attacker can deposit at the outdated (lower) price, then force the price upward by calling `updateRSETHPrice()`, and finally withdraw at the new higher price — extracting accrued yield that belongs to existing rsETH holders.

---

### Finding Description

`LRTOracle` stores the rsETH/ETH exchange rate in the state variable `rsETHPrice`. [1](#0-0) 

This value is only refreshed when `updateRSETHPrice()` is explicitly called: [2](#0-1) 

The function carries **no access control** — it is `public` and callable by any address.

When a user deposits via `LRTDepositPool.depositETH()` or `depositAsset()`, the internal `_beforeDeposit()` calls `getRsETHAmountToMint()`: [3](#0-2) 

`getRsETHAmountToMint()` divides the deposit value by the **stale cached** `lrtOracle.rsETHPrice()`: [4](#0-3) 

There is no call to `updateRSETHPrice()` inside the deposit path. The deposit pool simply reads whatever value was last written to `rsETHPrice`.

Meanwhile, `_updateRsETHPrice()` computes the true current price by reading live TVL from all node delegators and EigenLayer strategies: [5](#0-4) 

As staking rewards accrue (ETH rewards flow into the protocol), the real TVL grows but `rsETHPrice` remains frozen at its last-written value. The gap between the stale cached price and the true price is the exploitable window.

The withdrawal path in `LRTWithdrawalManager.initiateWithdrawal()` calls `getExpectedAssetAmount()` which uses the **current** oracle price at the time of the withdrawal request: [6](#0-5) 

This means a deposit made at the stale (lower) price and a withdrawal initiated after the price update (higher price) yields a net profit for the attacker at the expense of existing holders.

---

### Impact Explanation

**High — Theft of unclaimed yield.**

Existing rsETH holders accumulate yield as staking rewards increase the protocol's TVL. This yield is reflected in a rising `rsETHPrice`. An attacker who deposits at the stale lower price receives more rsETH than their deposit is worth at the true current rate. When the price is updated upward, the attacker's rsETH is now worth more than they paid, and they can withdraw the difference. The profit comes directly from the yield that should have accrued to pre-existing holders, diluting their share of the protocol's TVL.

At scale (large deposit amounts or repeated exploitation across multiple reward cycles), this can approach protocol insolvency.

---

### Likelihood Explanation

**Medium-High.**

- `updateRSETHPrice()` is public with no access control, so the attacker fully controls the timing of the price update.
- Staking rewards accrue continuously (Ethereum validator rewards, EigenLayer restaking rewards), so the stale-price window exists after every reward cycle.
- The `pricePercentageLimit` guard only blocks the price update call if the increase exceeds the configured threshold **and** `pricePercentageLimit > 0`. If the limit is unset (`== 0`), the guard is entirely bypassed per the condition `pricePercentageLimit > 0 && priceDifference > ...`. [7](#0-6) 

Even when the limit is set, small but profitable price movements within the threshold are freely exploitable. No special privileges, leaked keys, or external protocol compromise are required.

---

### Recommendation

1. **Atomically refresh the price inside the deposit flow.** Call `_updateRsETHPrice()` (or an equivalent internal read of live TVL) at the start of `depositETH()` / `depositAsset()` before computing `rsethAmountToMint`. This eliminates the stale-price window entirely.

2. **Alternatively, compute the mint amount from live TVL directly** rather than from the cached `rsETHPrice` state variable, so the deposit always uses the real-time exchange rate.

3. **Restrict `updateRSETHPrice()`** to trusted callers (e.g., a keeper or the manager role) so that the timing of price updates cannot be weaponized by an unprivileged attacker.

---

### Proof of Concept

**Setup:**
- Protocol TVL = 1000 ETH, rsETH supply = 1000, so true price = 1.000 ETH/rsETH.
- Staking rewards of 10 ETH accrue, making true TVL = 1010 ETH, true price = 1.010 ETH/rsETH.
- `rsETHPrice` is still cached at 1.000 ETH/rsETH (not yet updated).

**Attack steps:**

```
// Step 1: Attacker deposits 100 ETH at the stale price (1.000)
// getRsETHAmountToMint = (100 ETH * 1e18) / 1.000e18 = 100 rsETH
lrtDepositPool.depositETH{value: 100 ether}(100e18, "");
// Attacker receives 100 rsETH, but true value of 100 rsETH at 1.010 = 101 ETH

// Step 2: Attacker (or anyone) calls the public, permissionless price update
// New price = (1010 + 100) ETH / (1000 + 100) rsETH = 1110/1100 ≈ 1.00909 ETH/rsETH
// (slightly less than 1.010 because attacker's deposit dilutes the reward, but still > 1.000)
lrtOracle.updateRSETHPrice();

// Step 3: Attacker initiates withdrawal of 100 rsETH at the new price (~1.00909)
// expectedAssetAmount = 100 rsETH * 1.00909 = ~100.909 ETH
lrtWithdrawalManager.initiateWithdrawal(ETH_TOKEN, 100e18, "");

// Net profit: ~0.909 ETH extracted from existing holders' accrued yield
// Repeatable every reward cycle
```

The attacker-controlled entry path is:
1. `LRTDepositPool.depositETH()` — public, no auth [8](#0-7) 
2. `LRTOracle.updateRSETHPrice()` — public, no auth [2](#0-1) 
3. `LRTWithdrawalManager.initiateWithdrawal()` — public, no auth [9](#0-8)

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

**File:** contracts/LRTOracle.sol (L231-234)
```text
        uint256 totalETHInProtocol = _getTotalEthInProtocol();

        // calculate previousTVL using rsethSupply multiplied by rsETHPrice
        uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);
```

**File:** contracts/LRTOracle.sol (L256-257)
```text
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
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

**File:** contracts/LRTDepositPool.sol (L515-521)
```text
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTDepositPool.sol (L648-665)
```text
    function _beforeDeposit(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected
    )
        private
        view
        returns (uint256 rsethAmountToMint)
    {
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);
```

**File:** contracts/LRTWithdrawalManager.sol (L150-178)
```text
    function initiateWithdrawal(
        address asset,
        uint256 rsETHUnstaked,
        string calldata referralId
    )
        external
        override
        nonReentrant
        whenNotPaused
        onlySupportedAsset(asset)
        onlySupportedStrategy(asset)
    {
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }

        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);

        emit ReferralIdEmitted(referralId);
    }
```
