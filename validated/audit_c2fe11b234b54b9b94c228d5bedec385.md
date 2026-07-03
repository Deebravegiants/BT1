Audit Report

## Title
Stale Cross-Chain Rate Accepted Without Freshness Check Enables Protocol Insolvency - (`contracts/cross-chain/CrossChainRateReceiver.sol`)

## Summary

`CrossChainRateReceiver.getRate()` returns the stored `rate` unconditionally, ignoring the `lastUpdated` timestamp written on every `lzReceive` call. Every pool variant (`RSETHPool`, `RSETHPoolV2`, `RSETHPoolV3`, and their derivatives) calls `IOracle(rsETHOracle).getRate()` with no staleness guard. If the LayerZero update pipeline stalls, the stored rate silently ages while the true rsETH/ETH exchange rate rises with staking rewards, allowing an attacker to deposit ETH at the stale lower rate, receive excess wrsETH, and redeem it on L1 at the true higher rate — extracting value the protocol cannot cover.

## Finding Description

**Root cause — `CrossChainRateReceiver.getRate()` ignores `lastUpdated`:**

`lzReceive` writes `lastUpdated = block.timestamp` at line 97, but `getRate()` at lines 102–105 returns `rate` unconditionally with no reference to `lastUpdated`: [1](#0-0) 

**Consumption path — all pool variants call `getRate()` without a freshness check:**

`RSETHPool.getRate()` delegates directly to `IOracle(rsETHOracle).getRate()`: [2](#0-1) 

`RSETHPool.viewSwapRsETHAmountAndFee` (used by both ETH and token `deposit` overloads) computes `rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate` using the unchecked rate: [3](#0-2) 

`RSETHPoolV2.viewSwapRsETHAmountAndFee` follows the identical pattern and feeds `wrsETH.mint(msg.sender, rsETHAmount)`: [4](#0-3) [5](#0-4) 

`RSETHPoolV3.viewSwapRsETHAmountAndFee` is identical: [6](#0-5) [7](#0-6) 

A search for `lastUpdated`, `staleness`, `stale`, `maxAge`, or `freshness` across `contracts/pools/**` returns **zero matches** — no pool ever validates rate age.

**Why existing guards are insufficient:**

The `dailyMintLimit` in `RSETHPoolV2` and `RSETHPoolV3` resets every 24 hours and does not prevent multi-day exploitation: [8](#0-7) 

The `paused` flag requires privileged action to set and provides no automatic protection against a stale rate: [9](#0-8) 

## Impact Explanation

rsETH accrues staking rewards continuously, so its ETH price (`rate`) rises monotonically. A stale lower rate causes:

```
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate
```

A lower stale `rsETHToETHrate` produces a larger `rsETHAmount` than the deposited ETH warrants at the true rate. The L2 pool collects 1 ETH but the L1 must back more wrsETH than 1 ETH covers at the true rate. `RSETHPoolV2` and `RSETHPoolV3` mint new wrsETH on deposit, making supply inflation unbounded (subject only to the daily cap, which resets every 24 hours). `RSETHPool` transfers pre-held wrsETH, draining the pool faster than the ETH it collects can cover. Repeated over many depositors or days, this compounds into **protocol insolvency** (Critical).

## Likelihood Explanation

LayerZero message delivery can be delayed or stall due to network congestion, relayer downtime, or gas exhaustion on the destination chain — all without any on-chain signal. The rate update is push-only (triggered by the provider on L1); if the provider's keeper fails or is griefed, the L2 rate ages silently. A 30-day staleness window is realistic given no heartbeat enforcement. The attacker needs only a standard ETH deposit — a fully permissionless, production-supported entry point. No privileged access is required.

## Recommendation

Add a configurable `maxRateAge` to `CrossChainRateReceiver` and revert in `getRate()` if `block.timestamp - lastUpdated > maxRateAge`:

```solidity
uint256 public maxRateAge; // e.g. 24 hours

function getRate() external view returns (uint256) {
    require(block.timestamp - lastUpdated <= maxRateAge, "Rate is stale");
    return rate;
}
```

This single change propagates protection to every pool that calls `getRate()` through the `IOracle` interface, without modifying any pool contract.

## Proof of Concept

Deploy on an L2 fork (e.g., Arbitrum) where `CrossChainRateReceiver` is the `rsETHOracle`:

1. Assert `block.timestamp - lastUpdated > 7 days` (rate is stale).
2. Call `viewSwapRsETHAmountAndFee(10 ether)` — observe `rsETHAmount` computed at the stale lower rate.
3. Call `deposit{value: 10 ether}("poc")` as an unprivileged attacker — receive the inflated `rsETHAmount` of wrsETH.
4. Compute `received * trueRate / 1e18` (L1 redemption value) and assert it exceeds `10 ether`.
5. The difference is direct protocol loss: the pool collected 10 ETH but issued wrsETH redeemable for more than 10 ETH at the true rate.

The `assertGt(l1RedemptionValue, depositAmount)` assertion proves the invariant that wrsETH must be fully backed at the current exchange rate is violated whenever the stored rate is materially below the true rate. The Foundry fork test in the submission is a correct and reproducible demonstration of this path.

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

**File:** contracts/pools/RSETHPool.sol (L254-256)
```text
    function getRate() public view returns (uint256) {
        return IOracle(rsETHOracle).getRate();
    }
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

**File:** contracts/pools/RSETHPoolV2.sol (L60-63)
```text
    modifier whenNotPaused() {
        if (paused) revert ContractPaused();
        _;
    }
```

**File:** contracts/pools/RSETHPoolV2.sol (L72-94)
```text
    modifier limitDailyMint(uint256 amount) {
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
        }

        // Calculate the amount of rsETH that will be minted
        (uint256 rsETHAmount,) = viewSwapRsETHAmountAndFee(amount);
        uint256 currentDay = getCurrentDay();

        // If the current day is greater than the last mint day, reset the daily mint amount
        if (currentDay > lastMintDay) {
            lastMintDay = currentDay;
            dailyMintAmount = 0;
        }

        // Check if the daily mint amount plus the amount to mint is greater than the daily mint limit
        if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
            revert DailyMintLimitExceeded();
        }

        dailyMintAmount += rsETHAmount;
        _;
    }
```

**File:** contracts/pools/RSETHPoolV2.sol (L207-218)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused limitDailyMint(msg.value) {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
```

**File:** contracts/pools/RSETHPoolV2.sol (L225-233)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolV3.sol (L246-265)
```text
    function deposit(string memory referralId)
        external
        payable
        nonReentrant
        whenNotPaused
        limitDailyMint(msg.value, ETH_IDENTIFIER)
    {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
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
