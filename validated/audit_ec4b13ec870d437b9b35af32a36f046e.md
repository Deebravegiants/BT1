### Title
Lack of Access Control on `sendFunds()` in the MEV Reward Flow Allows Anyone to Trigger Premature Reward Distribution - (File: contracts/FeeReceiver.sol)

### Summary

`FeeReceiver.sendFunds()` has no access control modifier, allowing any external caller to flush the entire accumulated MEV/execution-layer reward balance from `FeeReceiver` into `LRTDepositPool` at any time. This is the direct analog of the M-07 vulnerability class: a reward-flow function that is publicly accessible and can be used to manipulate protocol state by unauthorized callers.

### Finding Description

`FeeReceiver` is the contract designated to receive MEV and execution-layer rewards on behalf of the protocol. It accumulates ETH over time via its `receive()` fallback. The function `sendFunds()` is intended to be called by an authorized party to forward those accumulated rewards to the deposit pool:

```solidity
// contracts/FeeReceiver.sol L53-58
function sendFunds() external {
    uint256 balance = address(this).balance;
    ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();
    emit MevRewardsAddedToTVL(balance);
}
```

There is no role check, no `onlyRole`, no `onlyLRTManager`, and no `whenNotPaused` guard. Any EOA or contract can call `sendFunds()` at any time. [1](#0-0) 

The destination, `LRTDepositPool.receiveFromRewardReceiver()`, is also an empty, unguarded `external payable` function:

```solidity
// contracts/LRTDepositPool.sol L61
function receiveFromRewardReceiver() external payable { }
``` [2](#0-1) 

Once ETH lands in `LRTDepositPool`, it is immediately counted in `getETHDistributionData()` as `ethLyingInDepositPool = address(this).balance`, which feeds directly into the rsETH price calculation via `getTotalAssetDeposits(ETH_TOKEN)` → `getRsETHAmountToMint()`. [3](#0-2) 

Critically, while the ETH sits in `FeeReceiver` it is **not** counted in the TVL (the comment in `getETHDistributionData()` explicitly states: *"rewards are not accounted here — it will automatically be accounted once it is moved from feeReceiver/rewardReceiver to depositPool"*). Moving it via `sendFunds()` therefore causes an immediate, discrete jump in rsETH price. [4](#0-3) 

### Impact Explanation

An attacker who holds rsETH can exploit the timing of reward distribution:

1. **Front-run large deposits**: Monitor the mempool for a large `depositETH()` call. Front-run it with `sendFunds()` to flush accumulated MEV rewards into the deposit pool, inflating the rsETH price. The victim depositor receives fewer rsETH tokens for the same ETH. Existing rsETH holders (including the attacker) receive a disproportionate share of the reward.

2. **Grief controlled reward schedules**: The protocol likely intends to distribute rewards at controlled intervals (e.g., after oracle updates or at off-peak times). An attacker can force distribution at any moment, disrupting the intended reward cadence and potentially causing oracle/price inconsistencies.

The ETH is not stolen outright, but the attacker can extract value by manipulating the rsETH price at the moment of a large deposit, effectively stealing yield from the incoming depositor and redirecting it to existing holders. This maps to **theft of unclaimed yield** (High) or at minimum **contract fails to deliver promised returns** (Low/Medium) depending on the accumulated reward size.

### Likelihood Explanation

- `sendFunds()` is a zero-argument, publicly callable function with no preconditions.
- `FeeReceiver` accumulates ETH continuously from validator MEV and execution-layer rewards; the balance is observable on-chain.
- Large deposits to `LRTDepositPool` are visible in the mempool.
- The attack requires only a standard ETH transaction to front-run; no special permissions, tokens, or flash loans are needed.
- Likelihood is **High**.

### Recommendation

Add an access control modifier to `sendFunds()` restricting it to the manager or operator role, consistent with how other fund-movement functions in the protocol are protected:

```solidity
function sendFunds() external onlyRole(LRTConstants.MANAGER) {
    uint256 balance = address(this).balance;
    ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();
    emit MevRewardsAddedToTVL(balance);
}
```

Additionally, consider adding caller validation to `LRTDepositPool.receiveFromRewardReceiver()` to ensure it can only be called from the registered `FeeReceiver` address, mirroring the pattern used in `NodeDelegator.sendETHFromDepositPoolToNDC()`:

```solidity
// NodeDelegator.sol L445-451 — the correct pattern
function sendETHFromDepositPoolToNDC() external payable override {
    if (msg.sender != lrtConfig.depositPool()) {
        revert InvalidETHSender();
    }
    ...
}
``` [5](#0-4) 

### Proof of Concept

1. `FeeReceiver` accumulates 10 ETH in MEV rewards (observable via `address(feeReceiver).balance`).
2. A whale submits a `depositETH{value: 1000 ETH}()` transaction to `LRTDepositPool`.
3. Attacker sees the pending transaction and front-runs with `FeeReceiver.sendFunds()`.
4. The 10 ETH moves from `FeeReceiver` to `LRTDepositPool`, increasing `ethLyingInDepositPool` by 10 ETH.
5. rsETH price increases by `10 / totalRsETHSupply * 1e18` before the whale's deposit is processed.
6. The whale's 1000 ETH mints fewer rsETH tokens than expected.
7. Attacker (existing rsETH holder) profits from the price increase at the whale's expense. [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/FeeReceiver.sol (L49-58)
```text
    /// @dev fallback to receive funds
    receive() external payable { }

    /// @dev send all rewards to deposit pool
    function sendFunds() external {
        uint256 balance = address(this).balance;
        ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();

        emit MevRewardsAddedToTVL(balance);
    }
```

**File:** contracts/LRTDepositPool.sol (L58-67)
```text
    receive() external payable { }

    /// @dev receive from RewardReceiver
    function receiveFromRewardReceiver() external payable { }

    /// @dev receive from LRTConverter
    function receiveFromLRTConverter() external payable { }

    /// @dev receive from NodeDelegator
    function receiveFromNodeDelegator() external payable { }
```

**File:** contracts/LRTDepositPool.sol (L464-467)
```text
    /// @dev provides ETH amount distribution data among depositPool, NDCs and eigenLayer
    /// @dev rewards are not accounted here
    /// it will automatically be accounted once it is moved from feeReceiver/rewardReceiver to depositPool
    function getETHDistributionData()
```

**File:** contracts/LRTDepositPool.sol (L480-480)
```text
        ethLyingInDepositPool = address(this).balance;
```

**File:** contracts/NodeDelegator.sol (L445-451)
```text
    function sendETHFromDepositPoolToNDC() external payable override {
        // only allow LRT deposit pool to send ETH to this contract
        if (msg.sender != lrtConfig.depositPool()) {
            revert InvalidETHSender();
        }

        emit ETHDepositFromDepositPool(msg.value);
```
