### Title
`FeeReceiver.sendFunds()` Callable by Anyone, Enabling MEV Reward Front-Running to Steal Unclaimed Yield - (File: contracts/FeeReceiver.sol)

### Summary
`FeeReceiver.sendFunds()` has no access control. Any external caller can trigger the transfer of all accumulated MEV/execution-layer rewards from `FeeReceiver` into `LRTDepositPool` at an arbitrary time. An attacker can sandwich this call — depositing ETH to mint rsETH at the pre-reward price, triggering `sendFunds()` to inflate TVL and thus the rsETH exchange rate, then redeeming rsETH at the elevated rate — capturing a disproportionate share of MEV rewards that belong to existing rsETH holders.

### Finding Description

`FeeReceiver.sendFunds()` is declared `external` with no role modifier, no `onlyOwner`, and no `onlyManager` guard:

```solidity
/// @dev send all rewards to deposit pool
function sendFunds() external {
    uint256 balance = address(this).balance;
    ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();
    emit MevRewardsAddedToTVL(balance);
}
``` [1](#0-0) 

Every other state-mutating function in `FeeReceiver` is gated behind `onlyRole(LRTConstants.MANAGER)` (e.g., `setDepositPool`), but `sendFunds()` is left completely open. [2](#0-1) 

When `sendFunds()` is called, all ETH held by `FeeReceiver` is forwarded to `LRTDepositPool.receiveFromRewardReceiver()`, which has no access control either and simply accepts the ETH:

```solidity
/// @dev receive from RewardReceiver
function receiveFromRewardReceiver() external payable { }
``` [3](#0-2) 

This ETH immediately becomes part of the protocol's TVL. The rsETH price (`rsETHPrice`) is computed by `LRTOracle` as `totalETHInProtocol / rsETH.totalSupply()`. Adding MEV rewards to the deposit pool therefore raises the rsETH exchange rate for anyone who redeems after the call.

### Impact Explanation

MEV/execution-layer rewards accumulate in `FeeReceiver` over time and represent unclaimed yield owed proportionally to **all current rsETH holders**. Because `sendFunds()` is permissionless, an attacker can:

1. Observe that `FeeReceiver` holds a meaningful ETH balance (e.g., 10 ETH in MEV rewards).
2. Deposit ETH into `LRTDepositPool` to mint rsETH at the current rate (before rewards are counted in TVL).
3. Call `sendFunds()` — the 10 ETH flows into the deposit pool, TVL rises, and the rsETH rate increases.
4. Initiate withdrawal / redeem rsETH at the now-higher rate.

The attacker extracts a share of the MEV rewards proportional to their freshly minted rsETH, diluting the yield that pre-existing holders should have received. This is **theft of unclaimed yield** from legitimate rsETH holders.

### Likelihood Explanation

- The attack requires no special role, no governance capture, and no leaked keys — only ETH to deposit.
- `FeeReceiver` accumulates rewards continuously from validator MEV and execution-layer tips; the balance is publicly visible on-chain.
- The attack is executable in a single block (deposit → `sendFunds()` → initiate withdrawal), or across blocks if a withdrawal delay exists (the rate is locked at initiation time in most withdrawal managers).
- Any sophisticated MEV bot or attacker monitoring the mempool can execute this profitably whenever the `FeeReceiver` balance is large enough to justify gas costs.

### Recommendation

Add an access-control modifier to `sendFunds()` so only an authorized role (e.g., `LRTConstants.MANAGER` or a dedicated `KEEPER_ROLE`) can trigger the reward flush:

```solidity
function sendFunds() external onlyRole(LRTConstants.MANAGER) {
    uint256 balance = address(this).balance;
    ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();
    emit MevRewardsAddedToTVL(balance);
}
```

Alternatively, restrict `receiveFromRewardReceiver()` in `LRTDepositPool` to only accept calls from the registered `FeeReceiver` address, so even if `sendFunds()` remains open, no third party can inject arbitrary ETH to manipulate TVL.

### Proof of Concept

```
// Attacker EOA, single transaction (or two blocks if withdrawal delay exists)

// Step 1: Deposit ETH, receive rsETH at current rate R0
LRTDepositPool.depositETH{value: 100 ether}(0, "");

// Step 2: Trigger MEV reward flush — no role required
FeeReceiver.sendFunds();
// FeeReceiver had 10 ETH → now in DepositPool → TVL increases → rsETH rate R1 > R0

// Step 3: Initiate withdrawal at rate R1
LRTWithdrawalManager.initiateWithdrawal(...);
// After delay, attacker receives more ETH than deposited, capturing a share of the 10 ETH MEV reward
// Existing rsETH holders receive proportionally less yield than they were owed
```

The root cause — `sendFunds()` lacking any access control — is directly analogous to the FrankenDAO `castVote` bug: a protocol function that triggers a fund movement is callable by any address without verifying the caller's eligibility, allowing an unprivileged actor to extract value from the protocol's reward pool.

### Citations

**File:** contracts/FeeReceiver.sol (L53-58)
```text
    function sendFunds() external {
        uint256 balance = address(this).balance;
        ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();

        emit MevRewardsAddedToTVL(balance);
    }
```

**File:** contracts/FeeReceiver.sol (L64-72)
```text
    /// @dev Set the deposit pool
    /// @param _depositPool Address of the deposit pool
    function setDepositPool(address _depositPool) external onlyRole(LRTConstants.MANAGER) {
        if (_depositPool == address(0)) revert InvalidEmptyValue();

        depositPool = _depositPool;

        emit DepositPoolSet(_depositPool);
    }
```

**File:** contracts/LRTDepositPool.sol (L61-61)
```text
    function receiveFromRewardReceiver() external payable { }
```
