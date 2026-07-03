### Title
Uninitialized `rsETHPrice` in `LRTOracle` Causes `initiateWithdrawal()` to Lock User rsETH Against Zero-Value Withdrawal Requests — (`contracts/LRTWithdrawalManager.sol` / `contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle.rsETHPrice` is a storage variable that defaults to `0` and is never set in `initialize()`. `LRTWithdrawalManager.getExpectedAssetAmount()` reads this value directly and multiplies by it, silently returning `0` when the price is uninitialized. `initiateWithdrawal()` has no guard against a zero `expectedAssetAmount`, so it accepts the request, locks the user's rsETH in the contract, and records a withdrawal entitlement of `0` underlying assets. When the request is later unlocked, `_calculatePayoutAmount()` returns the minimum of the stored `expectedAssetAmount` (0) and the current computed return, so the user permanently receives nothing while their rsETH is burned.

---

### Finding Description

`LRTOracle` is an upgradeable proxy. Its `initialize()` function sets only `lrtConfig` and emits an event; it does **not** set `rsETHPrice`. [1](#0-0) 

`rsETHPrice` is only written inside `_updateRsETHPrice()`, which is called by the permissionless `updateRSETHPrice()` or the manager-only `updateRSETHPriceAsManager()`. [2](#0-1) 

Until one of those is called, `rsETHPrice == 0`.

`LRTWithdrawalManager.getExpectedAssetAmount()` reads this stored value directly:

```solidity
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
``` [3](#0-2) 

When `rsETHPrice == 0`, the multiplication yields `0` and integer division returns `0` — no revert occurs.

`initiateWithdrawal()` calls `getExpectedAssetAmount()`, transfers the user's rsETH into the contract, and stores the withdrawal request — with no guard against `expectedAssetAmount == 0`:

```solidity
IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);
uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);
if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();
assetsCommitted[asset] += expectedAssetAmount;
_addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);
``` [4](#0-3) 

The stored `expectedAssetAmount = 0` is then used in `_calculatePayoutAmount()` at unlock time:

```solidity
uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
``` [5](#0-4) 

Because `request.expectedAssetAmount == 0`, the function always returns `0` regardless of what `rsETHPrice` is at unlock time. The user's rsETH is burned in `unlockQueue()` and they receive zero underlying assets. [6](#0-5) 

A secondary impact exists in `LRTDepositPool.getRsETHAmountToMint()`, which divides by `rsETHPrice` and reverts with division-by-zero when it is `0`, blocking all deposits:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [7](#0-6) 

---

### Impact Explanation

A user who calls `initiateWithdrawal()` while `rsETHPrice == 0` will:
1. Have their rsETH transferred to `LRTWithdrawalManager` (irreversible from the user's side).
2. Receive a withdrawal record with `expectedAssetAmount = 0`.
3. Receive `0` underlying assets when the withdrawal is completed.
4. Have their rsETH burned by the operator in `unlockQueue()`.

This constitutes **permanent, irrecoverable loss of user funds** — a Critical impact under the allowed scope.

The deposit path reverts (division by zero), causing **temporary freezing of deposits** — a Medium impact.

---

### Likelihood Explanation

The window exists between contract deployment/upgrade and the first successful call to `updateRSETHPrice()`. In a fresh deployment or after an upgrade that resets state, this window is real. The permissionless `updateRSETHPrice()` can be called by anyone, but if `pricePercentageLimit > 0` and `rsethSupply > 0`, the call reverts for non-managers due to the `PriceAboveDailyThreshold` check (because `highestRsethPrice` is also `0`, making any positive price appear to exceed the limit): [8](#0-7) 

This means the window can be extended if the manager is slow to act, and a user or attacker can exploit it during that window. Likelihood is **Low** but non-zero and reachable by any unprivileged user.

---

### Recommendation

1. **Initialize `rsETHPrice` in `initialize()`** to `1 ether` (the same value used when `rsethSupply == 0`).
2. **Add a zero-value guard in `initiateWithdrawal()`**:
   ```solidity
   if (expectedAssetAmount == 0) revert InvalidExpectedAssetAmount();
   ```
3. **Add a zero-value guard in `getExpectedAssetAmount()`** or in `_createUnlockParams()` to revert if `rsETHPrice == 0`.

---

### Proof of Concept

1. Deploy `LRTOracle` and call `initialize()`. Observe `rsETHPrice == 0`.
2. Deploy `LRTWithdrawalManager` pointing to the same `LRTConfig`.
3. As an unprivileged user, call `initiateWithdrawal(asset, 1 ether, "")` with 1 rsETH approved.
4. `getExpectedAssetAmount(asset, 1 ether)` returns `1e18 * 0 / assetPrice = 0`.
5. The check `0 > getAvailableAssetAmount(asset)` is `false` — no revert.
6. Withdrawal request is stored: `rsETHUnstaked = 1e18`, `expectedAssetAmount = 0`.
7. User's 1 rsETH is now locked in `LRTWithdrawalManager`.
8. Operator calls `unlockQueue()`. `_calculatePayoutAmount()` returns `min(0, currentReturn) = 0`.
9. `unlockQueue()` burns 1 rsETH from the contract.
10. User calls `completeWithdrawal()` and receives `0` assets.
11. User has permanently lost 1 rsETH with no recourse.

### Citations

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

**File:** contracts/LRTOracle.sol (L224-266)
```text
        if (highestRsethPrice == 0) {
            highestRsethPrice = rsETHPrice;
        }

        uint256 previousPrice = rsETHPrice;

        // get total ETH in the protocol (normalized to 1e18)
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
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

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
            }
```

**File:** contracts/LRTWithdrawalManager.sol (L162-176)
```text
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }

        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);

```

**File:** contracts/LRTWithdrawalManager.sol (L305-305)
```text
        if (rsETHBurned != 0) IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned);
```

**File:** contracts/LRTWithdrawalManager.sol (L590-594)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L833-834)
```text
        uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
        return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```
