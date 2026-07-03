### Title
Protocol Fee Deduction in `newRsETHPrice` Causes Premature Downside-Protection Trigger - (File: `contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle._updateRsETHPrice()` computes `newRsETHPrice` **after** subtracting the protocol fee from `totalETHInProtocol`, then uses that fee-adjusted price for the downside-protection threshold check. Because the fee deduction artificially lowers the computed price, the check can fire and pause the entire protocol even when the actual ETH-per-rsETH ratio has not crossed the configured threshold. This is the direct analog of M-8: a weighted/adjusted value is used in a safety check where the raw value should be used, producing a false-positive that blocks legitimate user operations.

---

### Finding Description

Inside `_updateRsETHPrice()`, the protocol fee is subtracted from `totalETHInProtocol` before the new price is computed:

```solidity
// contracts/LRTOracle.sol  lines 244-250
if (!protocolPaused && totalETHInProtocol > previousTVL) {
    uint256 rewardAmount = totalETHInProtocol - previousTVL;
    protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
}
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
``` [1](#0-0) 

That same fee-reduced `newRsETHPrice` is then fed directly into the downside-protection check:

```solidity
// contracts/LRTOracle.sol  lines 270-281
if (newRsETHPrice < highestRsethPrice) {
    uint256 diff = highestRsethPrice - newRsETHPrice;
    bool isPriceDecreaseOffLimit =
        pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

    if (isPriceDecreaseOffLimit) {
        if (!lrtDepositPool.paused()) lrtDepositPool.pause();
        if (!withdrawalManager.paused()) withdrawalManager.pause();
        _pause();
        return;
    }
}
``` [2](#0-1) 

The "true" price — what the ETH-per-rsETH ratio actually is before any fee is taken — is `totalETHInProtocol / rsethSupply`. The fee deduction makes `newRsETHPrice` strictly lower than that true price. When the true price sits just above the pause threshold but the fee-adjusted price sits just below it, the protocol is paused even though no actual loss of backing has occurred.

The entry point is `updateRSETHPrice()`, which is `public` with no access-control restriction beyond `whenNotPaused`:

```solidity
// contracts/LRTOracle.sol  line 87
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
``` [3](#0-2) 

Any external caller — including an unprivileged depositor or rsETH holder — can invoke this function at the moment the conditions are met.

---

### Impact Explanation

When the false-positive pause fires:

- `LRTDepositPool.depositETH()` / `depositAsset()` revert (`whenNotPaused`). [4](#0-3) 
- `LRTWithdrawalManager.initiateWithdrawal()` / `completeWithdrawal()` revert (`whenNot

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L244-250)
```text
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L270-281)
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
```

**File:** contracts/LRTDepositPool.sol (L83-93)
```text
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
