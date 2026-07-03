### Title
Unguarded Division by Zero on Uninitialized `rsETHPrice` Permanently Blocks Deposits Until Manual Intervention - (File: contracts/LRTDepositPool.sol, contracts/LRTOracle.sol)

### Summary
`LRTOracle.rsETHPrice` is a storage variable that defaults to `0` at deployment. `LRTDepositPool.getRsETHAmountToMint` divides by `lrtOracle.rsETHPrice()` without a zero-guard. Every L2 pool contract's `viewSwapRsETHAmountAndFee` similarly divides by `getRate()`, which reads `rsETHPrice` through the rate-provider chain. Until `updateRSETHPrice()` is called for the first time, every deposit path reverts with a division-by-zero panic, freezing the deposit surface of the entire protocol.

### Finding Description
`LRTOracle` is initialized without setting `rsETHPrice`:

```solidity
// contracts/LRTOracle.sol
function initialize(address lrtConfigAddr) external initializer {
    UtilLib.checkNonZeroAddress(lrtConfigAddr);
    lrtConfig = ILRTConfig(lrtConfigAddr);
    emit UpdatedLRTConfig(lrtConfigAddr);
}
```

`rsETHPrice` therefore starts at `0`. [1](#0-0) 

`LRTDepositPool.getRsETHAmountToMint` divides by this value unconditionally:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [2](#0-1) 

This is called by `_beforeDeposit`, which is called by both `depositETH` and `depositAsset`. Both public deposit entry points therefore revert with a division-by-zero panic whenever `rsETHPrice == 0`. [3](#0-2) 

The same zero-division path exists in every L2 pool contract. `viewSwapRsETHAmountAndFee` divides by `getRate()`:

```solidity
uint256 rsETHToETHrate = getRate();
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
``` [4](#0-3) 

`getRate()` calls `IOracle(rsETHOracle).getRate()`, which resolves through `RSETHRateProvider` or `RSETHMultiChainRateProvider` to `ILRTOracle(rsETHPriceOracle).rsETHPrice()`. [5](#0-4) 

No zero-check exists on `rsETHToETHrate` in the deposit path of `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, `RSETHPoolNoWrapper`, or `RSETHPool`. The reverse-swap path (`viewSwapAssetToPremintedRsETH`) does check for zero, but the forward deposit path does not. [6](#0-5) 

`updateRSETHPrice()` is public and callable by anyone, but it is not called during `initialize()`. The `_updateRsETHPrice` internal function sets `rsETHPrice = 1 ether` only when `rsethSupply == 0`, meaning the fix is available but not automatic. [7](#0-6) 

### Impact Explanation
All deposit entry points on both L1 (`LRTDepositPool.depositETH`, `depositAsset`) and every L2 pool contract revert with a division-by-zero panic until `updateRSETHPrice()` is called. This is a **temporary freezing of the deposit surface** of the entire protocol. Users cannot deposit ETH or LSTs; the protocol cannot grow its TVL. Existing depositors are unaffected (their funds are not at risk), but new capital is locked out.

**Impact: Medium — Temporary freezing of funds (deposit DoS).**

### Likelihood Explanation
The window exists between proxy deployment/upgrade and the first successful call to `updateRSETHPrice()`. Because `updateRSETHPrice()` is public, any actor (including the deployer) can close the window immediately. However:

- Deployment scripts that omit this call leave the protocol in a broken state for an indeterminate period.
- On a fresh upgrade where `rsETHPrice` is reset (e.g., storage collision or re-initialization bug), the same zero-state can recur.
- The absence of a zero-guard means the contract silently relies on an off-chain operational assumption rather than enforcing correctness on-chain.

**Likelihood: Low** — requires a deployment gap, but the gap is realistic and the missing guard is a structural weakness.

### Recommendation
1. In `LRTOracle.initialize`, call `_updateRsETHPrice()` or set `rsETHPrice = 1 ether` directly so the variable is never zero after initialization.
2. In `getRsETHAmountToMint`, add an explicit zero-check: `if (rsETHPrice == 0) revert PriceNotInitialized();`
3. In every `viewSwapRsETHAmountAndFee` implementation, mirror the guard already present in `viewSwapAssetToPremintedRsETH`: `if (rsETHToETHrate == 0) revert UnsupportedOracle();`

### Proof of Concept
1. Deploy `LRTOracle` proxy and call `initialize(lrtConfigAddr)`. `rsETHPrice` is `0`.
2. Deploy `LRTDepositPool` proxy pointing to the same `LRTConfig`.
3. Call `LRTDepositPool.depositETH{value: 1 ether}(0, "")`.
4. Execution reaches `getRsETHAmountToMint` → `(1e18 * assetPrice) / 0` → EVM division-by-zero panic → revert.
5. Call `LRTOracle.updateRSETHPrice()` (public, no access control). Because `rsethSupply == 0`, `rsETHPrice` is set to `1 ether`.
6. Repeat step 3 — deposit succeeds.

The same sequence applies to any L2 pool's `deposit()` function when the oracle backing `getRate()` returns `rsETHPrice == 0`.

### Citations

**File:** contracts/LRTOracle.sol (L64-68)
```text
    function initialize(address lrtConfigAddr) external initializer {
        UtilLib.checkNonZeroAddress(lrtConfigAddr);
        lrtConfig = ILRTConfig(lrtConfigAddr);
        emit UpdatedLRTConfig(lrtConfigAddr);
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

**File:** contracts/LRTDepositPool.sol (L86-92)
```text
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L299-308)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L391-401)
```text
        // Rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();
        if (rsETHToETHrate == 0) revert UnsupportedOracle();

        // Rate of token in ETH
        uint256 tokenToETHRate = token == ETH_IDENTIFIER ? 1e18 : IOracle(supportedTokenOracle[token]).getRate();
        if (tokenToETHRate == 0) revert UnsupportedOracle();

        // Calculate the amount of token user will get for the amount of rsETH
        tokenAmount = rsETHAmount * rsETHToETHrate / tokenToETHRate;
    }
```

**File:** contracts/cross-chain/RSETHRateProvider.sol (L27-28)
```text
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
```
