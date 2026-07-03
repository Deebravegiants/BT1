### Title
Deposit and Withdrawal Are Not Exact Inverses Due to Consistent Truncation in Both Directions - (`contracts/LRTDepositPool.sol` / `contracts/LRTWithdrawalManager.sol`)

---

### Summary

Both the deposit (rsETH minting) and withdrawal (asset redemption) paths in LRT-rsETH use integer division that truncates (rounds down). Because truncation is applied in both directions, a deposit followed by a withdrawal of the resulting rsETH will return fewer underlying assets than were originally deposited. The user silently loses the truncated remainder to the protocol on every round-trip.

---

### Finding Description

**Deposit path** — `LRTDepositPool.getRsETHAmountToMint`:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

The division truncates, so the user receives `floor(amount × assetPrice / rsETHPrice)` rsETH. [1](#0-0) 

**Withdrawal path** — `LRTWithdrawalManager.getExpectedAssetAmount`:

```solidity
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

The division again truncates, so the user receives `floor(rsETHAmount × rsETHPrice / assetPrice)` of the underlying asset. [2](#0-1) 

**Payout at unlock** — `LRTWithdrawalManager._calculatePayoutAmount`:

```solidity
uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
```

A third truncation is applied at the moment the withdrawal is unlocked, compounding the loss. [3](#0-2) 

**Concrete numeric example** (prices stable, no slashing):

| Step | Formula | Result |
|---|---|---|
| Deposit 5 wei of asset (`assetPrice = 1e18`, `rsETHPrice = 3e18`) | `floor(5 × 1e18 / 3e18)` | 1 rsETH minted |
| Withdraw 1 rsETH | `floor(1 × 3e18 / 1e18)` | 3 wei returned |
| **Net loss to user** | | **2 wei** |

The user deposited 5 wei and received 3 wei back — a 40 % loss on this micro-amount. At normal deposit sizes the relative loss is tiny (≤ 1 wei per operation), but it is systematic and always favours the protocol.

The `minRSETHAmountExpected` slippage guard on deposit only protects against the first truncation if the user computes the minimum correctly; it does not protect against the second truncation applied at withdrawal time. [4](#0-3) 

---

### Impact Explanation

**Low — Contract fails to deliver promised returns, but does not lose value.**

Every user who deposits an asset and later withdraws the resulting rsETH receives strictly fewer underlying tokens than they deposited whenever the division in either direction is inexact. The truncated remainder accrues to the protocol's TVL (it inflates `totalETHInProtocol` without a corresponding rsETH liability), benefiting all remaining rsETH holders at the expense of the withdrawing user. No funds are stolen outright, but the protocol does not deliver the full round-trip value it implicitly promises.

---

### Likelihood Explanation

**High.** The truncation fires on every deposit/withdrawal cycle where `amount × assetPrice` is not exactly divisible by `rsETHPrice`. Because `rsETHPrice` is a continuously updated WAD-precision value (`totalETHInProtocol / rsethSupply`), exact divisibility is essentially never guaranteed. Every user who completes a full deposit→withdraw round-trip is affected. [5](#0-4) 

---

### Recommendation

- **Short term**: Round the deposit conversion **down** (already done) and the withdrawal conversion **up** (currently also down). Changing `getExpectedAssetAmount` and `_calculatePayoutAmount` to use ceiling division (`mulDiv(…, Rounding.Up)`) for the asset-out calculation ensures the protocol never over-promises and the user receives at least as much as the rsETH is worth.
- **Short term**: Document the rounding behaviour clearly so integrators and users can account for the ≤ 1 wei per operation loss.
- **Long term**: Add invariant fuzz tests asserting that `getExpectedAssetAmount(asset, getRsETHAmountToMint(asset, X)) >= X - 1` for all valid inputs.

---

### Proof of Concept

1. Alice calls `LRTDepositPool.depositAsset(stETH, 5, 0, "")` when `assetPrice = 1e18`, `rsETHPrice = 3e18`.
2. `getRsETHAmountToMint` returns `floor(5 × 1e18 / 3e18) = 1`. Alice receives 1 rsETH.
3. Alice calls `LRTWithdrawalManager.initiateWithdrawal(stETH, 1, "")`.
4. `getExpectedAssetAmount` returns `floor(1 × 3e18 / 1e18) = 3`. Alice's request records `expectedAssetAmount = 3`.
5. After the delay, `completeWithdrawal` transfers 3 wei of stETH to Alice.
6. Alice deposited 5 wei and received 3 wei — a net loss of 2 wei with no price movement. [6](#0-5) [7](#0-6) [8](#0-7)

### Citations

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

**File:** contracts/LRTDepositPool.sol (L665-668)
```text
        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
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

**File:** contracts/LRTWithdrawalManager.sol (L824-834)
```text
    function _calculatePayoutAmount(
        WithdrawalRequest storage request,
        uint256 rsETHPrice,
        uint256 assetPrice
    )
        private
        view
        returns (uint256)
    {
        uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
        return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
```

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```
