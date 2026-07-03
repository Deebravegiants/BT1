### Title
rsETH Price Inflation via Open `receive()` + Public `updateRSETHPrice()` Enables First-Depositor Fund Theft - (File: contracts/LRTDepositPool.sol, contracts/LRTOracle.sol)

---

### Summary

An unprivileged attacker can perform a classic share-price inflation attack against `LRTDepositPool`. By making a dust first deposit, donating ETH directly to the pool via its open `receive()` fallback, and then calling the public `updateRSETHPrice()`, the attacker inflates `rsETHPrice` to an arbitrarily large value. Any subsequent depositor who passes `minRSETHAmountExpected = 0` receives 0 rsETH for their full ETH deposit, while the attacker—holding the entire rsETH supply—captures the victim's funds.

---

### Finding Description

**Step 1 — Dust first deposit**

`depositETH()` calls `_beforeDeposit()`, which calls `getRsETHAmountToMint()`: [1](#0-0) 

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

When `rsethSupply == 0`, `LRTOracle._updateRsETHPrice()` hard-codes `rsETHPrice = 1 ether`: [2](#0-1) 

So the first depositor of 1 wei ETH receives 1 wei rsETH (1:1). The `minAmountToDeposit` guard defaults to 0, so 1-wei deposits are accepted: [3](#0-2) 

**Step 2 — ETH donation via open `receive()`**

`LRTDepositPool` has an unrestricted `receive()`: [4](#0-3) 

`getETHDistributionData()` counts `address(this).balance` directly: [5](#0-4) 

Any ETH sent to the contract via `receive()` is immediately included in `totalETHInProtocol`.

**Step 3 — Public price update**

`updateRSETHPrice()` has no access control: [6](#0-5) 

The price increase guard only activates when `pricePercentageLimit > 0`; the default value is 0 (Solidity default for `uint256`), so the guard is inactive: [7](#0-6) 

After the donation of D wei, the new price becomes:

```
newRsETHPrice = (1 + D) * 1e18 / 1  ≈  D * 1e18
```

**Step 4 — Victim gets 0 rsETH**

For a victim depositing Y wei ETH:

```
rsethAmountToMint = Y * 1e18 / (D * 1e18) = Y / D
```

If `Y ≤ D`, integer division rounds to 0. The protocol-level check only reverts if `rsethAmountToMint < minRSETHAmountExpected`: [8](#0-7) 

When `minRSETHAmountExpected = 0`, the condition `0 < 0` is false, so the deposit succeeds and the victim's ETH is transferred to the pool while they receive 0 rsETH.

---

### Impact Explanation

The victim's ETH is permanently captured in the protocol. The attacker holds 1 wei rsETH representing 100% of the rsETH supply, which now backs `1 + D + Y` ETH. This constitutes **direct theft of user funds** — Critical severity.

---

### Likelihood Explanation

- `receive()` is open to all callers with no restriction.
- `updateRSETHPrice()` is public with no access control when `pricePercentageLimit == 0` (the default).
- `minAmountToDeposit` defaults to 0, allowing 1-wei seed deposits.
- Users or integrating contracts that pass `minRSETHAmountExpected = 0` (a common default for "accept any amount") are fully exposed.
- The attack is front-runnable: the attacker can observe a pending `depositETH` transaction in the mempool and execute the full sequence atomically.

---

### Recommendation

1. **Enforce a minimum rsETH output at the protocol level**: revert in `_beforeDeposit` if `rsethAmountToMint == 0`, regardless of `minRSETHAmountExpected`.
2. **Restrict `receive()`**: only accept ETH from known, trusted senders (e.g., `NodeDelegator`, `LRTConverter`, reward receivers). Reject arbitrary ETH donations.
3. **Set `pricePercentageLimit` to a non-zero value during initialization** so the price-increase guard is active from deployment.
4. **Set `minAmountToDeposit` to a meaningful floor** (e.g., 100 gwei) to prevent dust seed deposits.

---

### Proof of Concept

```
Preconditions: pricePercentageLimit == 0, minAmountToDeposit == 0

1. Attacker calls depositETH{value: 1}(0, "") 
   → rsethSupply = 1 wei, rsETHPrice = 1e18

2. Attacker sends 1 ETH directly to LRTDepositPool (via receive())
   → address(LRTDepositPool).balance = 1 + 1e18 wei

3. Attacker calls LRTOracle.updateRSETHPrice()
   → totalETHInProtocol = 1 + 1e18
   → newRsETHPrice = (1 + 1e18) * 1e18 / 1 ≈ 1e36

4. Victim calls depositETH{value: 0.999 ether}(0, "")
   → rsethAmountToMint = 0.999e18 * 1e18 / 1e36 = 0 (rounds down)
   → minRSETHAmountExpected = 0, so check passes
   → Victim's 0.999 ETH transferred to pool, 0 rsETH minted

5. Attacker holds 1 wei rsETH = 100% of supply = 1 + 1e18 + 0.999e18 ETH backing
   Net attacker profit ≈ 0.999 ETH (victim's deposit) minus 1 ETH donation cost
   → Attack becomes profitable when victim deposit ≥ donation amount
```

### Citations

**File:** contracts/LRTDepositPool.sol (L58-58)
```text
    receive() external payable { }
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

**File:** contracts/LRTDepositPool.sol (L657-659)
```text
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }
```

**File:** contracts/LRTDepositPool.sol (L665-669)
```text
        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L218-222)
```text
        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }
```

**File:** contracts/LRTOracle.sol (L252-265)
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
```
