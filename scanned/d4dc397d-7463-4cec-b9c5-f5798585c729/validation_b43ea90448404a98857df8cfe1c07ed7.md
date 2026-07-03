### Title
No `minAmountOut` in `instantWithdrawal()` Exposes Users to Oracle-Price Slippage — (File: contracts/LRTWithdrawalManager.sol)

---

### Summary
`LRTWithdrawalManager.instantWithdrawal()` calculates the asset amount to deliver to the user at execution time using live oracle prices, with no `minAmountOut` guard. A user who submits the transaction expecting a specific payout may receive materially less if the rsETH or asset oracle price moves between submission and on-chain execution, after their rsETH has already been burned.

---

### Finding Description

`instantWithdrawal()` is a publicly callable function that lets any rsETH holder burn their tokens in exchange for an immediate asset payout:

```solidity
function instantWithdrawal(
    address asset,
    uint256 rsETHUnstaked,
    string calldata referralId
) external nonReentrant whenNotPaused ...
{
    ...
    uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
    IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
    ...
    uint256 fee = (assetAmountUnlocked * instantWithdrawalFee) / 10_000;
    uint256 userAmount = assetAmountUnlocked - fee;
    _transferAsset(asset, msg.sender, userAmount);
}
``` [1](#0-0) 

`getExpectedAssetAmount` resolves the payout entirely from live oracle state:

```solidity
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
``` [2](#0-1) 

The sequence is:
1. `assetAmountUnlocked` is computed from the oracle at execution time.
2. rsETH is **burned** (irreversible).
3. The user receives `assetAmountUnlocked - fee`.

There is no `minAmountOut` parameter anywhere in the function signature or body. The user has no on-chain mechanism to reject a payout that is lower than what they observed off-chain when constructing the transaction.

By contrast, the standard deposit path in `LRTDepositPool` already carries this protection via `minRSETHAmountExpected`:

```solidity
function depositETH(uint256 minRSETHAmountExpected, string calldata referralId) ...
``` [3](#0-2) 

```solidity
if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
``` [4](#0-3) 

The same protection is absent from `instantWithdrawal`.

---

### Impact Explanation

**Impact: Low — Contract fails to deliver promised returns.**

A user previews the oracle price off-chain, constructs a transaction expecting `X` ETH/LST for `Y` rsETH, and submits. By the time the transaction is mined, the oracle price has moved (rsETH price down or asset price up). The user's rsETH is burned and they receive less than `X` with no recourse. The shortfall does not accrue to an attacker; it remains in the protocol as a rounding/price-movement benefit to remaining rsETH holders. The user suffers a real economic loss relative to their expectation, but the protocol does not become insolvent.

---

### Likelihood Explanation

**Likelihood: Medium.**

Oracle prices for rsETH and underlying LSTs update regularly. Any network congestion, mempool delay, or competing transaction that updates the oracle between a user's `eth_call` preview and their transaction's inclusion is sufficient to trigger the discrepancy. No special attacker capability is required; ordinary market conditions are enough.

---

### Recommendation

Add a `minAmountOut` parameter to `instantWithdrawal()` and revert if the computed payout falls below it:

```solidity
function instantWithdrawal(
    address asset,
    uint256 rsETHUnstaked,
    uint256 minAmountOut,          // <-- add this
    string calldata referralId
) external nonReentrant whenNotPaused ... {
    ...
    uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
    if (assetAmountUnlocked < minAmountOut) revert SlippageExceeded();
    IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
    ...
}
```

This mirrors the protection already present in `LRTDepositPool.depositETH` / `depositAsset`.

---

### Proof of Concept

1. rsETH oracle price = 1.05 ETH. User calls `instantWithdrawal(ETH, 10e18, "")` expecting ≈10.5 ETH.
2. Before the tx is mined, an oracle update sets rsETH price to 1.00 ETH.
3. `getExpectedAssetAmount` returns 10 ETH.
4. User's 10 rsETH is burned; user receives `10 ETH - fee` — 0.5 ETH less than expected.
5. No revert occurs; the user has no on-chain protection. [5](#0-4)

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

**File:** contracts/LRTDepositPool.sol (L667-669)
```text
        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
```
