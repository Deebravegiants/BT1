### Title
Permissionless `sendFunds()` in FeeReceiver Allows Yield Theft from Existing rsETH Holders - (File: contracts/FeeReceiver.sol)

### Summary

`FeeReceiver.sendFunds()` has no access control. Any external caller can trigger it at will, immediately flushing all accumulated MEV/execution-layer rewards into `LRTDepositPool`. Because `LRTDepositPool.getTotalAssetDeposits` reads live on-chain balances and `LRTOracle.rsETHPrice()` is derived from that total, the rsETH exchange rate rises the moment the ETH lands in the pool. An attacker who deposits ETH just before calling `sendFunds()` captures a disproportionate share of those rewards at the expense of long-term holders.

### Finding Description

`FeeReceiver.sendFunds()` is declared `external` with no role check:

```solidity
function sendFunds() external {
    uint256 balance = address(this).balance;
    ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();
    emit MevRewardsAddedToTVL(balance);
}
``` [1](#0-0) 

The ETH sent to `LRTDepositPool` is immediately counted in `getETHDistributionData()` via `address(this).balance`: [2](#0-1) 

That balance feeds `getTotalAssetDeposits`, which feeds `LRTOracle.rsETHPrice()`, which is the denominator used in `getRsETHAmountToMint`: [3](#0-2) 

There is no deposit fee in `LRTDepositPool`; `_beforeDeposit` computes `rsethAmountToMint` purely from the oracle price with no fee deduction: [4](#0-3) 

### Impact Explanation

An attacker deposits ETH at the pre-reward rsETH price (receiving more rsETH per ETH), then calls `sendFunds()` to push accumulated MEV rewards into the pool, raising the rsETH price. When the attacker later redeems their rsETH through `LRTWithdrawalManager`, they receive more ETH than they deposited, having captured a share of rewards that should have accrued to long-standing holders. This is **theft of unclaimed yield** (High impact per the allowed scope).

### Likelihood Explanation

- `FeeReceiver` accumulates ETH passively from MEV and execution-layer rewards; its balance is publicly visible on-chain.
- `sendFunds()` requires no privilege, no signature, and no special state.
- `LRTDepositPool.depositETH` is open to any caller with no deposit fee.
- The only friction is the withdrawal delay in `LRTWithdrawalManager`, which reduces but does not eliminate profitability, especially when the FeeReceiver holds a large accumulated balance.
- Likelihood: **Medium** (requires capital and waiting through the withdrawal delay, but is otherwise trivially executable).

### Recommendation

1. Add an access-control modifier to `sendFunds()` so only a trusted operator or keeper role can trigger it:
   ```solidity
   function sendFunds() external onlyRole(LRTConstants.MANAGER) { ... }
   ```
2. Alternatively, send rewards via a private/Flashbots relay so the transaction cannot be front-run.
3. Consider a deposit fee or a minimum holding period before withdrawal to make the attack economically unattractive even if `sendFunds()` remains permissionless.

### Proof of Concept

**Setup:** FeeReceiver holds 100 ETH in accumulated MEV rewards. Total protocol ETH = 10,000 ETH. rsETH supply = 9,500 rsETH. rsETH price ≈ 1.0526 ETH/rsETH.

1. **Attacker deposits 10,000 ETH** via `LRTDepositPool.depositETH`. At the current price they receive `10,000 / 1.0526 ≈ 9,500 rsETH`. Total ETH = 20,000, rsETH supply = 19,000, price unchanged.

2. **Attacker calls `FeeReceiver.sendFunds()`**. 100 ETH flows into the deposit pool. Total ETH = 20,100, rsETH supply = 19,000. New price = `20,100 / 19,000 ≈ 1.0579 ETH/rsETH`.

3. **Attacker initiates withdrawal** of their 9,500 rsETH. They receive `9,500 × 1.0579 ≈ 10,050 ETH`.

4. **Net gain:** ~50 ETH stolen from the 100 ETH reward that should have been distributed pro-rata to the 9,500 pre-existing rsETH holders (Alice et al.), who now only benefit from the remaining ~50 ETH of the reward.

The attack scales linearly: the larger the attacker's deposit relative to existing TVL, the greater the fraction of rewards they capture.

### Citations

**File:** contracts/FeeReceiver.sol (L53-58)
```text
    function sendFunds() external {
        uint256 balance = address(this).balance;
        ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();

        emit MevRewardsAddedToTVL(balance);
    }
```

**File:** contracts/LRTDepositPool.sol (L480-481)
```text
        ethLyingInDepositPool = address(this).balance;

```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
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
