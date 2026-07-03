Audit Report

## Title
Missing User-Controlled Slippage Protection in L2 Pool `deposit()` Functions - (File: `contracts/pools/RSETHPoolV3.sol`)

## Summary
The `deposit()` functions in `RSETHPoolV3` and `RSETHPoolV2ExternalBridge` accept no `minRSETHAmountExpected` parameter, so depositors have no on-chain protection against receiving fewer rsETH tokens than the rate they observed off-chain. The L1 `LRTDepositPool` correctly implements this guard via `_beforeDeposit`, creating a concrete and confirmed asymmetry. A depositor who queries the rate and submits a transaction that mines after a routine oracle update silently receives less rsETH than expected with no recourse.

## Finding Description
**Root cause:** `RSETHPoolV3.deposit(string)` and `RSETHPoolV3.deposit(address,uint256,string)` compute the minted rsETH amount entirely from the live oracle rate at execution time and mint unconditionally: [1](#0-0) [2](#0-1) 

The rate is fetched from `rsETHOracle` at call time with no floor check: [3](#0-2) 

The same pattern exists in `RSETHPoolV2ExternalBridge.deposit()`: [4](#0-3) 

**Contrast with L1:** `LRTDepositPool._beforeDeposit` explicitly reverts if the minted amount falls below the caller-supplied minimum: [5](#0-4) 

**Exploit flow:**
1. User calls `viewSwapRsETHAmountAndFee(1 ether)` off-chain; oracle reports `rsETHToETHrate = 1.05e18`, yielding ≈0.952 rsETH.
2. User submits `deposit{value: 1 ether}("ref")`.
3. Before the transaction mines, the oracle is updated to `rsETHToETHrate = 1.10e18` (routine update).
4. Transaction executes: `rsETHAmount = 1e18 * 1e18 / 1.10e18 ≈ 0.909 rsETH` — ~4.5% less than expected.
5. No revert; user silently receives 0.909 rsETH. Deposited ETH is consumed in full.

No adversary is required; this is triggered by any routine oracle update that lands between the user's off-chain quote and on-chain execution.

## Impact Explanation
**Low — Contract fails to deliver promised returns, but doesn't lose value.**

The deposited ETH/LST is not stolen; it enters the pool. However, the user receives materially fewer rsETH tokens than the rate they observed and relied upon, with no on-chain mechanism to prevent or revert this outcome. This matches the allowed impact: *"Contract fails to deliver promised returns, but doesn't lose value."*

## Likelihood Explanation
No special attacker capability is required. The oracle rate for rsETH is updated periodically by the oracle operator as a normal protocol operation. On any L2 with short block times and frequent oracle updates, the window between a user's `eth_call` quote and transaction inclusion is sufficient for the rate to shift. This is a routine, non-adversarial scenario that affects every depositor who relies on the quoted rate. The condition is repeatable and requires no coordination.

## Recommendation
Add a `minRSETHAmountExpected` parameter to both `deposit()` overloads in `RSETHPoolV3` and to `deposit()` in `RSETHPoolV2ExternalBridge`, mirroring the L1 pattern:

```solidity
function deposit(string memory referralId, uint256 minRSETHAmountExpected)
    external payable nonReentrant whenNotPaused
    limitDailyMint(msg.value, ETH_IDENTIFIER)
{
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minRSETHAmountExpected) revert MinimumAmountToReceiveNotMet();
    ...
}
```

Apply the same pattern to the token overload and to `RSETHPoolV2ExternalBridge.deposit()`.

## Proof of Concept
**Foundry fork test outline:**

```solidity
function test_depositSlippageNoProtection() public {
    // 1. Record oracle rate before deposit
    uint256 rateBefore = pool.getRate(); // e.g. 1.05e18
    uint256 expectedRsETH = 1e18 * 1e18 / rateBefore; // ~0.952e18

    // 2. Simulate oracle update (rate increases to 1.10e18)
    vm.prank(oracleUpdater);
    oracle.setRate(1.10e18);

    // 3. User's deposit executes at new rate
    vm.prank(user);
    pool.deposit{value: 1 ether}("ref");

    uint256 actualRsETH = wrsETH.balanceOf(user); // ~0.909e18
    // Assert user received less than expected with no revert
    assertLt(actualRsETH, expectedRsETH);
}
```

The test requires no privileged access beyond the oracle updater performing its routine update. The deposit succeeds silently and the user receives fewer rsETH than the off-chain quote indicated.

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L258-262)
```text
        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);
```

**File:** contracts/pools/RSETHPoolV3.sol (L286-290)
```text
        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);
```

**File:** contracts/pools/RSETHPoolV3.sol (L299-308)
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

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L289-301)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused limitDailyMint(msg.value) {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L667-669)
```text
        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
```
