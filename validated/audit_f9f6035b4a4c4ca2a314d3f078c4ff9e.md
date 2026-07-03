Audit Report

## Title
Stale Rate in `CrossChainRateReceiver.getRate()` Causes Pool to Overpay rsETH to Depositors, Depleting Inventory — (`contracts/cross-chain/CrossChainRateReceiver.sol`)

## Summary

`CrossChainRateReceiver.getRate()` returns the stored `rate` with no staleness guard despite tracking `lastUpdated` on every `lzReceive` call. Both `RSETHPool` and `RSETHPoolNoWrapper` call `getRate()` unconditionally to price every ETH deposit, then transfer pre-existing rsETH from their own inventory. When the LayerZero update is delayed and the true L1 rsETH/ETH rate has risen, the stale (lower) rate causes the pool to transfer more rsETH per ETH than the bridged ETH will regenerate on L1, gradually depleting the pool's rsETH inventory.

## Finding Description

`CrossChainRateReceiver.getRate()` returns the raw stored `rate` with no staleness guard:

```solidity
// CrossChainRateReceiver.sol L103-105
function getRate() external view returns (uint256) {
    return rate;
}
```

`lastUpdated` is written on every `lzReceive` call at L97 but is never read by any internal logic or by callers — it is only a public state variable.

Both pool contracts delegate pricing entirely to this oracle without any freshness check:

- `RSETHPool.viewSwapRsETHAmountAndFee()` L316: `uint256 rsETHToETHrate = getRate();`
- `RSETHPoolNoWrapper.viewSwapRsETHAmountAndFee()` L282: `uint256 rsETHToETHrate = getRate();`

Both pools then transfer pre-existing rsETH from their own balance — they do not mint:

- `RSETHPool` L275: `IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);`
- `RSETHPoolNoWrapper` L241: `rsETH.safeTransfer(msg.sender, rsETHAmount);`

**Arithmetic of the overpayment:**

| Scenario | Rate used | rsETH out for 1 ETH |
|---|---|---|
| Stale (1.05e18) | 1.05e18 | `1e18 / 1.05e18` ≈ 0.9524 rsETH |
| Fresh (1.10e18) | 1.10e18 | `1e18 / 1.10e18` ≈ 0.9091 rsETH |
| **Overpayment per ETH** | | **≈ 0.0433 rsETH** |

The 1 ETH bridged to L1 will only regenerate ≈ 0.9091 rsETH at the true rate. The pool already paid out 0.9524, so it is short ≈ 0.0433 rsETH per ETH deposited during the stale window. This shortfall comes directly from the pool's pre-loaded rsETH inventory. The difference between the stale and true rate represents yield that has accrued on L1 since the last oracle update — yield that depositors capture at the pool's expense.

## Impact Explanation

The pool's rsETH inventory is depleted faster than the bridged ETH replenishes it. The rsETH given out was already minted and backed on L1, so no unbacked tokens are created, but the pool systematically gives away rsETH at a discount relative to the true L1 rate. The spread loss is the accrued yield since the last oracle update, captured by depositors. This maps to **High — Theft of unclaimed yield**: the yield accrued on rsETH since the last `lzReceive` update is extracted by depositors rather than remaining in the pool's inventory. No attacker action is required; any depositor during the stale window benefits automatically.

## Likelihood Explanation

LayerZero message delays are a known operational reality (network congestion, relayer downtime). rsETH accrues yield continuously, so even a few hours of staleness during a high-accrual period creates a measurable spread. No special privileges or attacker setup are required — any user calling `deposit()` during the stale window automatically receives the overpayment. The pool has no circuit-breaker, no staleness check, and no minimum rate delta guard.

## Recommendation

Add a configurable maximum staleness threshold and revert in `getRate()` if exceeded:

```solidity
uint256 public maxStaleness; // e.g. 24 hours

function getRate() external view returns (uint256) {
    require(block.timestamp - lastUpdated <= maxStaleness, "Rate is stale");
    return rate;
}
```

Alternatively, expose `lastUpdated` to callers and enforce the check in the pool contracts before pricing a deposit.

## Proof of Concept

```solidity
// Fork test (Arbitrum fork)
function testStaleRateOverpay() public {
    MockReceiver oracle = new MockReceiver();
    oracle.setRate(1.05e18);                          // stale rate
    oracle.setLastUpdated(block.timestamp - 2 days);  // 2 days stale

    RSETHPoolNoWrapper pool = /* deploy with oracle */;
    rsETH.transfer(address(pool), 10e18);             // pre-load inventory

    // User deposits 1 ETH at stale rate
    uint256 balBefore = rsETH.balanceOf(user);
    pool.deposit{value: 1e18}("ref");
    uint256 staleOut = rsETH.balanceOf(user) - balBefore;
    // staleOut ≈ 0.9524e18

    // Simulate rate update to true value
    oracle.setRate(1.10e18);
    oracle.setLastUpdated(block.timestamp);

    // Same deposit at fresh rate
    uint256 balBefore2 = rsETH.balanceOf(user2);
    pool.deposit{value: 1e18}("ref");
    uint256 freshOut = rsETH.balanceOf(user2) - balBefore2;
    // freshOut ≈ 0.9091e18

    assertGt(staleOut, freshOut);
    // Difference ≈ 0.0433e18 rsETH per ETH — pool inventory shortfall
    // Pool received 2 ETH but can only regenerate 2 * 0.9091 = 1.8182 rsETH on L1
    // Pool paid out 0.9524 + 0.9091 = 1.8615 rsETH — net loss of 0.0433 rsETH
}
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L95-105)
```text
        rate = _rate;

        lastUpdated = block.timestamp;

        emit RateUpdated(_rate);
    }

    /// @notice Gets the last stored rate in the contract
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/pools/RSETHPool.sol (L273-276)
```text
        feeEarnedInETH += fee;

        IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);

```

**File:** contracts/pools/RSETHPool.sol (L311-319)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L239-242)
```text
        feeEarnedInETH += fee;

        rsETH.safeTransfer(msg.sender, rsETHAmount);

```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L277-286)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
    }
```
