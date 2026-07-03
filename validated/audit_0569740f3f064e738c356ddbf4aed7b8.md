The exploit path is concrete. Let me verify the exact lines for the key guards and the mint flow.

### Title
Fee Minting via Permissionless `sendFunds()` + `updateRSETHPrice()` Exhausts Shared RSETH Daily Mint Limit, DoS-ing User Deposits — (`contracts/FeeReceiver.sol`, `contracts/LRTOracle.sol`, `contracts/RSETH.sol`)

---

### Summary

An unprivileged attacker can call the permissionless `FeeReceiver.sendFunds()` followed by `LRTOracle.updateRSETHPrice()` to trigger protocol fee minting. Because fee minting goes through `RSETH.mint()`, it consumes the same `maxMintAmountPerDay` / `currentPeriodMintedAmount` counter that user deposits use. If the fee mint exhausts the daily limit, all subsequent user `depositETH()` / `depositAsset()` calls revert with `DailyMintLimitExceeded` for up to 24 hours.

The claimed impact of **Critical. Protocol insolvency** is overstated. The correct impact is **Medium. Temporary freezing of funds** (deposit DoS for up to 24 hours).

---

### Finding Description

**Step 1 — Permissionless TVL injection**

`FeeReceiver.sendFunds()` carries no access control:

```solidity
function sendFunds() external {
    uint256 balance = address(this).balance;
    ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();
    emit MevRewardsAddedToTVL(balance);
}
``` [1](#0-0) 

`LRTDepositPool.receiveFromRewardReceiver()` is equally unguarded:

```solidity
function receiveFromRewardReceiver() external payable { }
``` [2](#0-1) 

Any EOA can push the entire FeeReceiver ETH balance into the deposit pool, immediately increasing `totalETHInProtocol`.

**Step 2 — Permissionless oracle update triggers fee mint**

`updateRSETHPrice()` is `public whenNotPaused` — no role required: [3](#0-2) 

Inside `_updateRsETHPrice()`, when `totalETHInProtocol > previousTVL` and the protocol is not paused, a protocol fee is computed and minted:

```solidity
uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);
_checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
``` [4](#0-3) 

**Step 3 — Fee mint consumes the shared RSETH daily limit**

`RSETH.mint()` applies `checkDailyMintLimit(amount)` to every caller, including the oracle's fee mint:

```solidity
function mint(address to, uint256 amount)
    external
    onlyRole(LRTConstants.MINTER_ROLE)
    whenNotPaused
    checkDailyMintLimit(amount)
``` [5](#0-4) 

The modifier increments `currentPeriodMintedAmount` and reverts if the limit is exceeded:

```solidity
if (currentPeriodMintedAmount + amount > maxMintAmountPerDay) {
    revert DailyMintLimitExceeded(currentPeriodMintedAmount + amount, maxMintAmountPerDay);
}
currentPeriodMintedAmount += amount;
``` [6](#0-5) 

There is **no separate counter** for fee mints vs. user deposit mints. Both share `currentPeriodMintedAmount` and `maxMintAmountPerDay`.

**Step 4 — User deposits are DoS'd**

After the fee mint consumes the remaining daily allowance, any call to `depositETH()` or `depositAsset()` that internally calls `_mintRsETH()` → `RSETH.mint()` will revert with `DailyMintLimitExceeded` until the 24-hour period resets. [7](#0-6) 

---

### Impact Explanation

**Medium. Temporary freezing of funds.**

User deposits are blocked for up to 24 hours. No funds are stolen and no permanent state corruption occurs; the period resets automatically. The claimed "Critical. Protocol insolvency" is not accurate — the protocol remains solvent and withdrawals are unaffected. The correct classification is temporary DoS of the deposit path.

---

### Likelihood Explanation

- Both `sendFunds()` and `updateRSETHPrice()` are callable by any EOA with zero privilege.
- FeeReceiver accumulates MEV/execution-layer rewards continuously; the attacker only needs to wait for sufficient balance.
- The price-threshold guard (`PriceAboveDailyThreshold`) only fires when `pricePercentageLimit > 0` **and** the price increase exceeds that limit. If `pricePercentageLimit == 0` (unset), the guard is entirely bypassed. [8](#0-7) 
- Even when the limit is set, the attacker can time the call so the MEV reward amount stays within the threshold, or split across multiple oracle update cycles.
- The oracle-level `maxFeeMintAmountPerDay` guard (`_checkAndUpdateDailyFeeMintLimit`) is a **separate** cap that limits how much fee the oracle mints per day, but it does not prevent the fee from consuming RSETH's shared `maxMintAmountPerDay`. [9](#0-8) 

---

### Recommendation

1. **Separate the mint counters.** Introduce a dedicated counter in `RSETH` (or in the oracle) for protocol fee mints, distinct from the user-deposit daily limit. Fee mints should not consume `maxMintAmountPerDay`.
2. **Access-control `sendFunds()`** to restrict callers to authorized operators/managers, preventing arbitrary timing of TVL injections.
3. **Alternatively**, ensure `maxMintAmountPerDay` is sized to accommodate both expected user deposit volume and the maximum possible daily fee mint (`maxFeeMintAmountPerDay`), and document this dependency explicitly.

---

### Proof of Concept

```solidity
// Preconditions:
//   - FeeReceiver holds 100 ETH of accumulated MEV rewards
//   - RSETH.maxMintAmountPerDay = X (e.g. 1000 rsETH)
//   - RSETH.currentPeriodMintedAmount = X - feeRsETH (just below limit)
//   - protocolFeeInBPS > 0, protocol not paused, pricePercentageLimit == 0

// Attack:
feeReceiver.sendFunds();          // pushes 100 ETH into depositPool, TVL increases
lrtOracle.updateRSETHPrice();     // detects TVL increase, mints feeRsETH to treasury
                                  // RSETH.currentPeriodMintedAmount now == X

// Victim:
depositPool.depositETH{value: 1 ether}(0, "");
// Reverts: DailyMintLimitExceeded(X + userRsETH, X)
// User deposits are frozen for up to 24 hours
```

### Citations

**File:** contracts/FeeReceiver.sol (L53-58)
```text
    function sendFunds() external {
        uint256 balance = address(this).balance;
        ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();

        emit MevRewardsAddedToTVL(balance);
    }
```

**File:** contracts/LRTDepositPool.sol (L61-61)
```text
    function receiveFromRewardReceiver() external payable { }
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

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L197-210)
```text
    function _checkAndUpdateDailyFeeMintLimit(uint256 feeAmount) internal {
        // Reset the period if it's unset or a day has passed
        if (block.timestamp >= feePeriodStartTime + 1 days) {
            currentPeriodMintedFeeAmount = 0;
            feePeriodStartTime = getCurrentPeriodStartTime();
        }

        // Check if minting would exceed the daily limit
        if (currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay) {
            revert DailyFeeMintLimitExceeded(currentPeriodMintedFeeAmount + feeAmount, maxFeeMintAmountPerDay);
        }

        currentPeriodMintedFeeAmount += feeAmount;
    }
```

**File:** contracts/LRTOracle.sol (L256-265)
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
```

**File:** contracts/LRTOracle.sol (L301-307)
```text
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
```

**File:** contracts/RSETH.sol (L50-54)
```text
        if (currentPeriodMintedAmount + amount > maxMintAmountPerDay) {
            revert DailyMintLimitExceeded(currentPeriodMintedAmount + amount, maxMintAmountPerDay);
        }

        currentPeriodMintedAmount += amount;
```

**File:** contracts/RSETH.sol (L229-237)
```text
    function mint(
        address to,
        uint256 amount
    )
        external
        onlyRole(LRTConstants.MINTER_ROLE)
        whenNotPaused
        checkDailyMintLimit(amount)
    {
```
