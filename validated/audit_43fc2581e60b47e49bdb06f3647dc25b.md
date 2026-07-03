### Title
Stale `rsETHPrice` Used in Deposit Minting Without Prior Price Update — (File: contracts/LRTDepositPool.sol)

---

### Summary
`LRTDepositPool.depositAsset()` and `depositETH()` compute the rsETH mint amount using `lrtOracle.rsETHPrice()`, a cached storage value, without first calling `updateRSETHPrice()`. When protocol TVL increases (e.g., staking rewards accrue in EigenLayer), the stored price becomes stale-low. New depositors receive more rsETH than their fair share, diluting existing holders and stealing their unclaimed yield.

---

### Finding Description
`LRTOracle` stores `rsETHPrice` as a persistent state variable updated only when `updateRSETHPrice()` is explicitly called. Both deposit entry points in `LRTDepositPool` read this cached value directly:

```solidity
// LRTDepositPool.sol – getRsETHAmountToMint()
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

`updateRSETHPrice()` is a separate public function that recomputes the price from live TVL data. It is never invoked atomically inside `depositAsset()` or `depositETH()`. Between reward accrual events and the next `updateRSETHPrice()` call, `rsETHPrice` is stale-low (the actual per-share value is higher than stored). During this window, the mint formula over-issues rsETH to new depositors.

The same stale read affects `LRTWithdrawalManager.initiateWithdrawal()`, which calls `getExpectedAssetAmount()`:

```solidity
// LRTWithdrawalManager.sol – getExpectedAssetAmount()
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

A stale-low price here under-pays withdrawers, compounding the harm to existing holders.

---

### Impact Explanation
When `rsETHPrice` is stale-low (rewards have accrued but the price has not been updated), a depositor receives:

```
rsethMinted = depositValue / stalePrice  >  depositValue / truePrice
```

The excess rsETH represents a claim on yield that belongs to existing holders. After `updateRSETHPrice()` is eventually called, the new depositor's inflated rsETH balance is worth exactly what they paid plus a portion of the accrued yield they did not earn. This is a direct transfer of unclaimed yield from existing rsETH holders to the new depositor.

**Impact: High — Theft of unclaimed yield.**

---

### Likelihood Explanation
- `updateRSETHPrice()` is called off-chain (by a bot or keeper), not atomically with deposits. There is always a non-zero window between reward accrual and price update.
- The function is public, so an attacker can observe a pending `updateRSETHPrice()` transaction in the mempool and front-run it with a large deposit at the stale price.
- No special privileges are required; any unprivileged depositor can exploit this.
- The `pricePercentageLimit` guard in `_updateRsETHPrice()` can cause the price update to revert if the increase exceeds the threshold (unless called by a manager), potentially extending the stale window significantly.

**Likelihood: Medium.**

---

### Recommendation
Call `updateRSETHPrice()` (or an equivalent internal price refresh) atomically at the start of `depositAsset()`, `depositETH()`, and `initiateWithdrawal()` before any mint/burn amount is computed. To avoid reverting when the price is already current or within tolerance, the internal `_updateRsETHPrice()` logic should be refactored so that a no-op update (price unchanged) does not revert, analogous to the remediation in the reference report (changing `revert` to an `if` guard).

---

### Proof of Concept

1. Protocol holds 1000 ETH of TVL; 1000 rsETH minted; `rsETHPrice = 1e18` (1:1).
2. EigenLayer rewards accrue: TVL becomes 1010 ETH. True rsETH price = `1.01e18`. `updateRSETHPrice()` has not yet been called; `rsETHPrice` remains `1e18`.
3. Attacker calls `depositETH{value: 10 ether}(0, "")`. `getRsETHAmountToMint` computes `10e18 * 1e18 / 1e18 = 10 rsETH`. Fair amount at true price: `10e18 / 1.01e18 ≈ 9.9 rsETH`. Attacker receives ~0.1 extra rsETH.
4. `updateRSETHPrice()` is called. New TVL = 1020 ETH, total supply = 1010 rsETH, new price = `~1.0099e18`. Attacker's 10 rsETH is now worth `10 * 1.0099e18 / 1e18 ≈ 10.099 ETH` — more than the 10 ETH deposited.
5. The ~0.099 ETH gain came directly from the 10 ETH of yield that belonged to the original 1000 rsETH holders.

**Entry path:** `LRTDepositPool.depositETH()` → `_beforeDeposit()` → `getRsETHAmountToMint()` → `lrtOracle.rsETHPrice()` (stale). [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

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

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
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

**File:** contracts/LRTWithdrawalManager.sol (L580-594)
```text
    function getExpectedAssetAmount(
        address asset,
        uint256 amount
    )
        public
        view
        override
        returns (uint256 underlyingToReceive)
    {
        // setup oracle contract
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```
