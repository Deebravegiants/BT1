### Title
`onlyLRTOperator` Can Swap Assets for ETH Bypassing Pause - (File: `contracts/LRTDepositPool.sol`)

### Summary
`swapAssetForETHWithinDepositPool()` in `LRTDepositPool.sol` is missing the `whenNotPaused` modifier, allowing the `LRTOperator` role to extract ETH from the deposit pool even when the protocol is paused. The same omission exists on `swapETHForAssetWithinDepositPool()`.

### Finding Description
`LRTDepositPool` inherits `PausableUpgradeable` and correctly guards user-facing entry points (`depositETH`, `depositAsset`) with `whenNotPaused`. However, two operator-callable fund-movement functions are unguarded:

- `swapAssetForETHWithinDepositPool()` (L166–197): restricted to `onlyLRTOperator`, pulls LST from the caller and sends ETH from the pool's balance to the caller. No `whenNotPaused`.
- `swapETHForAssetWithinDepositPool()` (L128–159): restricted to `onlyLRTOperator`, pulls ETH from the caller and sends LST from the pool's balance to the caller. No `whenNotPaused`. [1](#0-0) [2](#0-1) 

The pause on `LRTDepositPool` is not merely cosmetic. `LRTOracle._updateRsETHPrice()` automatically triggers it when the rsETH price drops beyond the configured threshold, and the oracle itself checks `lrtDepositPool.paused()` to decide whether to take protocol fees: [3](#0-2) [4](#0-3) 

During such an auto-pause the operator can still call `swapAssetForETHWithinDepositPool()`, transferring ETH out of the pool at oracle-quoted prices — prices that may be stale or in flux at the exact moment the circuit-breaker fired.

### Impact Explanation
The pause is the protocol's primary circuit-breaker. When it fires (automatically or manually), all fund movements are supposed to halt. Because `swapAssetForETHWithinDepositPool()` lacks `whenNotPaused`, the operator can drain ETH from the deposit pool while users are locked out of deposits and withdrawals. At minimum this defeats the invariant that a paused protocol moves no funds; at worst, if the pause was triggered by a price anomaly, the operator executes swaps at a rate that may not reflect true value.

Impact: **Low — Contract fails to deliver promised returns** (pause guarantee broken); escalates toward **Medium** if the swap occurs while oracle prices are in an anomalous state that caused the pause.

### Likelihood Explanation
The `LRTDepositPool` pause is triggered automatically by `LRTOracle._updateRsETHPrice()` whenever the rsETH price falls beyond `pricePercentageLimit`. This is a realistic, non-adversarial scenario. Any operator who calls `swapAssetForETHWithinDepositPool()` during that window — even without malicious intent — bypasses the pause.

### Recommendation
Add `whenNotPaused` to both swap functions:

```solidity
function swapAssetForETHWithinDepositPool(
    address fromAsset,
    uint256 fromAssetAmount,
    uint256 minETHAmountExpected
)
    external
    nonReentrant
    whenNotPaused          // <-- add
    onlyLRTOperator
    onlySupportedERC20Token(fromAsset)
{ ... }

function swapETHForAssetWithinDepositPool(
    address toAsset,
    uint256 minToAssetAmount
)
    external
    payable
    nonReentrant
    whenNotPaused          // <-- add
    onlyLRTOperator
    onlySupportedERC20Token(toAsset)
{ ... }
```

### Proof of Concept
1. `LRTOracle.updateRSETHPrice()` detects a price drop beyond `pricePercentageLimit` and calls `lrtDepositPool.pause()`.
2. `LRTDepositPool` is now paused; `depositETH` and `depositAsset` revert for all users.
3. The operator calls `swapAssetForETHWithinDepositPool(stETH, largeAmount, 0)`.
4. The function has no `whenNotPaused` check — it executes, pulling `stETH` from the operator and sending ETH from the pool to the operator.
5. ETH exits the deposit pool while the protocol is in its emergency-paused state, violating the pause invariant. [5](#0-4) [2](#0-1) [6](#0-5)

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

**File:** contracts/LRTDepositPool.sol (L128-159)
```text
    function swapETHForAssetWithinDepositPool(
        address toAsset,
        uint256 minToAssetAmount
    )
        external
        payable
        nonReentrant
        onlyLRTOperator
        onlySupportedERC20Token(toAsset)
    {
        // checks
        uint256 ethAmountSent = msg.value;

        if (ethAmountSent == 0) {
            revert ZeroAssetAmount();
        }

        uint256 returnAmount = getSwapETHToAssetReturnAmount(toAsset, ethAmountSent);

        if (minToAssetAmount > returnAmount) {
            revert MinAssetAmountNotMet();
        }

        if (IERC20(toAsset).balanceOf(address(this)) < returnAmount) {
            revert NotEnoughAssetToTransfer();
        }

        // interactions
        IERC20(toAsset).safeTransfer(msg.sender, returnAmount);

        emit ETHSwappedForLST(ethAmountSent, toAsset, returnAmount);
    }
```

**File:** contracts/LRTDepositPool.sol (L166-197)
```text
    function swapAssetForETHWithinDepositPool(
        address fromAsset,
        uint256 fromAssetAmount,
        uint256 minETHAmountExpected
    )
        external
        nonReentrant
        onlyLRTOperator
        onlySupportedERC20Token(fromAsset)
    {
        if (fromAssetAmount == 0) {
            revert ZeroAssetAmount();
        }

        // checks
        uint256 returnAmount = getSwapAssetForETHReturnAmount(fromAsset, fromAssetAmount);

        if (minETHAmountExpected > returnAmount) {
            revert MinAssetAmountNotMet();
        }

        if (address(this).balance < returnAmount) {
            revert NotEnoughETHToTransfer();
        }

        IERC20(fromAsset).safeTransferFrom(msg.sender, address(this), fromAssetAmount);

        (bool success,) = payable(msg.sender).call{ value: returnAmount }("");
        if (!success) revert EthTransferFailed();

        emit AssetSwappedForETH(fromAsset, fromAssetAmount, returnAmount);
    }
```

**File:** contracts/LRTOracle.sol (L236-244)
```text
        IPausable lrtDepositPool = IPausable(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable withdrawalManager = IPausable(lrtConfig.getContract(LRTConstants.LRT_WITHDRAW_MANAGER));

        // determine if the protocol is active (not paused)
        bool protocolPaused = lrtDepositPool.paused() || withdrawalManager.paused() || paused;

        // only take fee if TVL increased and protocol is not paused
        uint256 protocolFeeInETH = 0;
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
```

**File:** contracts/LRTOracle.sol (L270-282)
```text
        if (newRsETHPrice < highestRsethPrice) {
            uint256 diff = highestRsethPrice - newRsETHPrice;
            // normalizing to 1e18
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

            // if price decrease is off limit, pause the protocol (unless it's already paused)
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
            }
```
