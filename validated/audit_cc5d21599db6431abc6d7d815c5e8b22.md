### Title
Division by Zero in `viewSwapRsETHAmountAndFee` When Oracle Returns Zero Rate - (File: contracts/pools/RSETHPool.sol, RSETHPoolNoWrapper.sol, RSETHPoolV2NBA.sol, RSETHPoolV2ExternalBridge.sol, RSETHPoolV3WithNativeChainBridge.sol)

### Summary
Multiple L2 pool contracts divide by `rsETHToETHrate` in `viewSwapRsETHAmountAndFee` without checking whether the oracle-returned rate is zero. The `CrossChainRateReceiver` oracle initializes `rate` to the default `uint256` value of `0` and only updates it upon receiving a LayerZero cross-chain message. If the oracle has not yet received its first rate update, every `deposit()` call panics with a Solidity division-by-zero error, temporarily bricking all user deposits into the pool.

### Finding Description
`RSETHPool.getRate()`, `RSETHPoolNoWrapper.getRate()`, `RSETHPoolV2NBA.getRate()`, `RSETHPoolV2ExternalBridge.getRate()`, and `RSETHPoolV3WithNativeChainBridge.getRate()` all delegate to `IOracle(rsETHOracle).getRate()`. [1](#0-0) 

When the oracle is `CrossChainRateReceiver`, its `rate` storage variable starts at `0` and is only written by `lzReceive`: [2](#0-1) 

There is no lower-bound validation on `_rate` before it is stored, and the initial value is `0`.

Each pool's `viewSwapRsETHAmountAndFee` then performs:

```solidity
uint256 rsETHToETHrate = getRate();
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;  // panics if rsETHToETHrate == 0
``` [3](#0-2) [4](#0-3) [5](#0-4) 

No zero-check guards this division. Notably, the same contracts *do* guard the reverse-swap path: [6](#0-5) 

This inconsistency confirms the developers were aware of the zero-rate risk in some code paths but missed it in `viewSwapRsETHAmountAndFee`.

### Impact Explanation
Any call to `deposit()` (ETH or token variant) invokes `viewSwapRsETHAmountAndFee`, which panics. The transaction reverts, returning the user's ETH, but no deposit can succeed. All L2 pool deposit functionality is temporarily frozen until the oracle receives a non-zero rate. This maps to **Low — Contract fails to deliver promised returns, but doesn't lose value**, with potential escalation to **Medium — Temporary freezing of funds** if the oracle remains at zero for an extended period (e.g., cross-chain messaging delay or failure).

### Likelihood Explanation
The window exists at every fresh deployment of a pool paired with a `CrossChainRateReceiver` oracle, before the first cross-chain rate message arrives. It also re-opens if a zero-value rate payload is ever relayed (no validation in `lzReceive`). The entry path is fully unprivileged: any user calling `deposit()` triggers the panic.

### Recommendation
1. Add a zero-rate guard in every `viewSwapRsETHAmountAndFee` variant, consistent with the existing guard in `viewSwapAssetToPremintedRsETH`:
   ```solidity
   if (rsETHToETHrate == 0) revert UnsupportedOracle();
   ```
2. Add validation in `CrossChainRateReceiver.lzReceive` to reject a zero rate:
   ```solidity
   if (_rate == 0) revert InvalidRate();
   ```

### Proof of Concept
1. Deploy `CrossChainRateReceiver` (or any pool pointing to a freshly deployed one). `rate` is `0`.
2. Call `RSETHPool.deposit{value: 1 ether}("ref")`.
3. Execution reaches `viewSwapRsETHAmountAndFee` → `getRate()` returns `0` → `amountAfterFee * 1e18 / 0` → Solidity panic `0x12` (division by zero).
4. Transaction reverts; user cannot deposit. All subsequent deposit attempts fail identically until the oracle is updated.

### Citations

**File:** contracts/pools/RSETHPool.sol (L253-256)
```text
    /// @dev Gets the rate from the rsETHOracle
    function getRate() public view returns (uint256) {
        return IOracle(rsETHOracle).getRate();
    }
```

**File:** contracts/pools/RSETHPool.sol (L315-320)
```text
        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
    }
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L93-105)
```text
        uint256 _rate = abi.decode(_payload, (uint256));

        rate = _rate;

        lastUpdated = block.timestamp;

        emit RateUpdated(_rate);
    }

    /// @notice Gets the last stored rate in the contract
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L282-286)
```text
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPoolV2NBA.sol (L128-133)
```text
        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L399-403)
```text
    function viewSwapAssetToPremintedRsETH(uint256 rsETHAmount) public view returns (uint256 ethAmount) {
        // Rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();
        if (rsETHToETHrate == 0) revert UnsupportedOracle();

```
