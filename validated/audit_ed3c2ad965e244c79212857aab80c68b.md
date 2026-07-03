### Title
Missing Minimum Output Check in `instantWithdrawal()` Exposes Users to Oracle-Rate Slippage - (File: contracts/LRTWithdrawalManager.sol)

### Summary
The `instantWithdrawal()` function in `LRTWithdrawalManager` burns a user's rsETH and transfers assets calculated from live oracle prices at execution time, with no `minAssetAmount` parameter. If the oracle rate moves adversely between transaction submission and execution, the user receives fewer assets than expected while their rsETH is permanently burned.

### Finding Description
`instantWithdrawal()` computes the asset payout entirely at execution time via `getExpectedAssetAmount()`, which divides `lrtOracle.rsETHPrice()` by `lrtOracle.getAssetPrice(asset)`. There is no caller-supplied minimum acceptable output. The function signature is:

```solidity
function instantWithdrawal(
    address asset,
    uint256 rsETHUnstaked,
    string calldata referralId
) external ...
```

The payout calculation at execution time:

```solidity
uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
...
uint256 fee = (assetAmountUnlocked * instantWithdrawalFee) / 10_000;
uint256 userAmount = assetAmountUnlocked - fee;
_transferAsset(asset, msg.sender, userAmount);
```

The `getExpectedAssetAmount` view:

```solidity
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

The code's own NatSpec comment acknowledges execution-time variability: *"Uses the fee set at execution time. Managers can raise it right before this call, making withdrawals cost more than expected."* The same execution-time risk applies to the oracle rate, but no guard exists for it.

By contrast, `LRTDepositPool.depositETH()` and `depositAsset()` both accept a `minRSETHAmountExpected` parameter and enforce it in `_beforeDeposit()`, demonstrating the protocol is aware of the pattern and applies it on the deposit side but not on the instant-withdrawal side.

### Impact Explanation
A user who previews the expected output off-chain (via `getExpectedAssetAmount`) and then submits `instantWithdrawal()` may have their rsETH burned while receiving materially fewer assets than anticipated if the oracle rate updates between submission and inclusion. The rsETH burn is irreversible; the user cannot retry at the original rate. This constitutes the contract failing to deliver the promised return on the user's rsETH.

**Impact: Low — Contract fails to deliver promised returns, but doesn't lose value.**

### Likelihood Explanation
The LRT oracle (`LRTOracle`) aggregates prices from multiple LST price feeds and is updated by operators. Oracle updates are routine and can occur at any time. On Ethereum mainnet, where `LRTWithdrawalManager` lives, blocks are produced every ~12 seconds and oracle updates can land in the same block or the block immediately before a user's transaction. Any rsETH holder who calls `instantWithdrawal()` is exposed to this risk on every invocation.

### Recommendation
Add a `minAssetAmount` parameter to `instantWithdrawal()` and revert if the computed payout falls below it:

```solidity
function instantWithdrawal(
    address asset,
    uint256 rsETHUnstaked,
    uint256 minAssetAmount,   // <-- add this
    string calldata referralId
) external ... {
    ...
    uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
    uint256 fee = (assetAmountUnlocked * instantWithdrawalFee) / 10_000;
    uint256 userAmount = assetAmountUnlocked - fee;
    if (userAmount < minAssetAmount) revert SlippageExceeded();
    IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
    ...
}
```

The burn should also be moved after the slippage check so that no rsETH is destroyed if the check fails.

### Proof of Concept

1. Alice holds 10 rsETH. She calls `getExpectedAssetAmount(ETH, 10e18)` off-chain and sees she will receive 10.5 ETH (rsETH price = 1.05 ETH, asset price = 1 ETH). She submits `instantWithdrawal(ETH, 10e18, "ref")`.
2. Before Alice's transaction is included, the LRT oracle is updated: rsETH price drops to 1.00 ETH (e.g., a slashing event is reflected).
3. Alice's transaction executes. `getExpectedAssetAmount` now returns 10 ETH. After a 0.5% fee, she receives 9.95 ETH.
4. Alice's 10 rsETH is burned. She expected ~10.5 ETH but received 9.95 ETH — a ~0.55 ETH shortfall with no recourse.
5. Had a `minAssetAmount = 10.4e18` guard been present, the transaction would have reverted and Alice's rsETH would have been preserved.

**Root cause lines:** [1](#0-0) 

**No minimum output guard — rsETH burned before any slippage check:** [2](#0-1) 

**Oracle-dependent payout calculation with no floor:** [3](#0-2) 

**Contrast: deposit side correctly enforces a minimum:** [4](#0-3)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L212-253)
```text
    function instantWithdrawal(
        address asset,
        uint256 rsETHUnstaked,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedAsset(asset)
        onlySupportedStrategy(asset)
        onlyInstantWithdrawalAllowed(asset)
    {
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }
        if (IERC20(lrtConfig.rsETH()).balanceOf(msg.sender) < rsETHUnstaked) revert NotEnoughRsETH();
        uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
        IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
        ILRTUnstakingVault unstakingVault = ILRTUnstakingVault(lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT));
        if (assetAmountUnlocked > unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)) {
            revert CantInstantWithdrawMoreThanAvailable();
        }

        unstakingVault.redeem(asset, assetAmountUnlocked);

        uint256 fee = (assetAmountUnlocked * instantWithdrawalFee) / 10_000;
        uint256 userAmount = assetAmountUnlocked - fee;

        address feeRecipient = instantWithdrawalFeeRecipient;
        if (feeRecipient == address(0)) {
            // Backwards-compatible default: send fees to the protocol treasury
            feeRecipient = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
        }
        if (fee > 0) {
            _transferAsset(asset, feeRecipient, fee);
            emit InstantWithdrawalFeeCollected(msg.sender, asset, fee);
        }

        _transferAsset(asset, msg.sender, userAmount);
        emit ReferralIdEmitted(referralId);
        emit AssetWithdrawalFinalized(msg.sender, asset, rsETHUnstaked, userAmount);
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

**File:** contracts/LRTDepositPool.sol (L648-670)
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

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
    }
```
