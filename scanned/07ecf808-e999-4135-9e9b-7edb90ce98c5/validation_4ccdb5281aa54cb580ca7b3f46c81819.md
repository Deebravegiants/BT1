### Title
Permissionless `FeeReceiver.sendFunds()` Enables Yield Theft via Deposit Frontrunning — (`contracts/FeeReceiver.sol`)

---

### Summary

`FeeReceiver.sendFunds()` carries no access control. Any external caller can trigger a lump-sum MEV/execution-layer reward flush into `LRTDepositPool` at will. An attacker can deposit ETH into `LRTDepositPool` immediately before calling `sendFunds()`, diluting the reward share of all pre-existing rsETH holders and capturing yield they did not earn.

---

### Finding Description

`FeeReceiver` accumulates MEV and execution-layer rewards passively over time via its `receive()` fallback. The `sendFunds()` function is unrestricted:

```solidity
// contracts/FeeReceiver.sol L53-58
function sendFunds() external {
    uint256 balance = address(this).balance;
    ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();
    emit MevRewardsAddedToTVL(balance);
}
``` [1](#0-0) 

When this ETH lands in `LRTDepositPool`, it is immediately counted in `getETHDistributionData()` via `address(this).balance`:

```solidity
// contracts/LRTDepositPool.sol L480
ethLyingInDepositPool = address(this).balance;
``` [2](#0-1) 

`_getTotalEthInProtocol()` in `LRTOracle` aggregates this balance when computing the new rsETH price:

```solidity
// contracts/LRTOracle.sol L341-343
uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
totalETHInProtocol += totalAssetAmt.mulWad(assetER);
``` [3](#0-2) 

`updateRSETHPrice()` is also publicly callable (no role restriction):

```solidity
// contracts/LRTOracle.sol L87-89
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
``` [4](#0-3) 

The new rsETH price is computed as `(totalETHInProtocol - protocolFee) / rsethSupply`:

```solidity
// contracts/LRTOracle.sol L250
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
``` [5](#0-4) 

**Attack sequence:**

1. Attacker observes `FeeReceiver.balance = R` (accumulated MEV rewards).
2. Attacker calls `LRTDepositPool.depositETH()` with a large amount `X`, receiving rsETH at the current price. TVL and supply both increase proportionally; price is unchanged.
3. Attacker calls `FeeReceiver.sendFunds()`. `R` ETH is added to the deposit pool TVL; rsETH supply is unchanged.
4. Attacker (or anyone) calls `LRTOracle.updateRSETHPrice()`. The new price reflects the inflated TVL.
5. Attacker's rsETH is now worth `X + X·R/(T+X)` ETH, where `T` is the pre-deposit TVL.
6. Attacker initiates withdrawal through `LRTWithdrawalManager` and recovers principal plus stolen yield after the EigenLayer delay.

**Numerical example:**

| State | TVL | rsETH Supply | Price |
|---|---|---|---|
| Before attack | 1000 ETH | 1000 rsETH | 1.000 |
| After attacker deposits 100 ETH | 1100 ETH | 1100 rsETH | 1.000 |
| After `sendFunds()` adds 10 ETH | 1110 ETH | 1100 rsETH | 1.00909 |

Attacker's 100 rsETH → 100.909 ETH. **Profit: 0.909 ETH stolen from existing holders** (who should have received the full 10 ETH reward but receive only 9.09 ETH).

The structural root cause is identical to the referenced report: a lump-sum reward is distributed to whoever holds the relevant position *at the moment of distribution*, not to those who earned it over time. Because `sendFunds()` is permissionless, the attacker controls the timing.

---

### Impact Explanation

**High — Theft of unclaimed yield.** Existing rsETH holders lose a fraction of every MEV/execution-layer reward batch proportional to the attacker's deposit size relative to TVL. The larger the accumulated `FeeReceiver` balance and the larger the attacker's deposit, the greater the theft. MEV bots can automate this continuously, draining yield from long-term holders.

---

### Likelihood Explanation

**Medium.** The attack requires locking up capital for the EigenLayer withdrawal delay (~7 days). However:
- `sendFunds()` and `updateRSETHPrice()` are both permissionless, so no privileged access is needed.
- The attack is fully on-chain and automatable by MEV searchers.
- Profitability scales with the size of accumulated rewards; large MEV events (e.g., post-merge MEV spikes) make the attack highly attractive.
- No flash loan is needed; the attacker only needs to hold capital for the withdrawal delay period.

---

### Recommendation

Restrict `sendFunds()` to an authorized role (e.g., `MANAGER` or `DEFAULT_ADMIN_ROLE`):

```solidity
function sendFunds() external onlyRole(LRTConstants.MANAGER) {
    uint256 balance = address(this).balance;
    ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();
    emit MevRewardsAddedToTVL(balance);
}
```

This prevents an attacker from controlling the timing of reward distribution. Alternatively, implement a streaming reward model (similar to Synthetix `rewardRate`) so rewards accrue continuously rather than in lump sums, eliminating the timing advantage entirely.

---

### Proof of Concept

```solidity
// Attacker contract (single transaction up to step 3; withdrawal is separate)
contract Attacker {
    LRTDepositPool pool;
    FeeReceiver feeReceiver;
    LRTOracle oracle;

    function attack() external payable {
        // Step 1: Deposit ETH at current rsETH price
        pool.depositETH{value: msg.value}(0, "");

        // Step 2: Flush accumulated MEV rewards into deposit pool
        feeReceiver.sendFunds();

        // Step 3: Update rsETH price to reflect new TVL
        oracle.updateRSETHPrice();

        // Attacker now holds rsETH worth more than deposited.
        // Initiate withdrawal via LRTWithdrawalManager and claim after delay.
    }
}
``` [1](#0-0) [6](#0-5) [4](#0-3)

### Citations

**File:** contracts/FeeReceiver.sol (L53-58)
```text
    function sendFunds() external {
        uint256 balance = address(this).balance;
        ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();

        emit MevRewardsAddedToTVL(balance);
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

**File:** contracts/LRTDepositPool.sol (L480-480)
```text
        ethLyingInDepositPool = address(this).balance;
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L341-343)
```text
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```
