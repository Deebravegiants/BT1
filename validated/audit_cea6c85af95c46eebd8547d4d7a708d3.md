Audit Report

## Title
Stale Cross-Chain Rate Consumed Without Freshness Check Enables Over-Minting of rsETH — (`contracts/pools/RSETHPoolV3.sol`, `contracts/cross-chain/CrossChainRateReceiver.sol`)

## Summary
`CrossChainRateReceiver.getRate()` returns the last stored rate with no staleness check against `lastUpdated`. `RSETHPoolV3.deposit()` and `viewSwapRsETHAmountAndFee()` consume this rate directly to compute and mint rsETH with no independent freshness validation. Because rsETH/ETH rate increases monotonically from staking yield, any window where the L2 rate lags the L1 rate allows a depositor to receive more rsETH than the current rate entitles them to, capturing yield that belongs to existing rsETH holders.

## Finding Description
**Rate broadcast path (L1 → L2):**

1. `MultiChainRateProvider.updateRate()` (line 108) carries no access control — any caller can trigger a rate push to L2 via LayerZero. The function reads `getLatestRate()` and sends it to all registered `rateReceivers`.

2. `CrossChainRateReceiver.lzReceive()` (lines 93–97) decodes the payload, writes `rate = _rate` and `lastUpdated = block.timestamp`. `getRate()` (lines 103–105) returns `rate` unconditionally — `lastUpdated` is stored but never checked.

3. `RSETHPoolV3.getRate()` (lines 235–237) delegates directly to `IOracle(rsETHOracle).getRate()`, which is the receiver above. No staleness guard exists.

4. `RSETHPoolV3.viewSwapRsETHAmountAndFee()` (lines 299–308) computes `rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate` using the unchecked rate.

5. `RSETHPoolV3.deposit()` (lines 246–265) mints `rsETHAmount` directly from step 4.

6. The `limitDailyMint` modifier (lines 96–125) also calls `viewSwapRsETHAmountAndFee()` to compute the rsETH cap, so the daily limit is evaluated in rsETH units against the inflated stale-rate amount — it does not independently cap ETH-equivalent value.

**Attack path:**
- rsETH/ETH rate on L1 increases by Δ (continuous staking yield accrual).
- Attacker stuffs L2 blocks with high-priority transactions to delay the LayerZero relayer's `lzReceive()` call, keeping `rate` at the pre-increase value `r_stale < r_current`.
- Attacker calls `deposit()` during the staleness window: `rsETHAmount = ETH * 1e18 / r_stale > ETH * 1e18 / r_current`.
- Excess rsETH minted = `ETH * 1e18 * (1/r_stale − 1/r_current)` is unbacked at the current L1 rate, diluting existing holders' accrued yield.

Block stuffing on low-fee L2 chains (Arbitrum, Optimism, Base) is substantially cheaper than on Ethereum mainnet, making the delay window economically controllable.

## Impact Explanation
Every unit of excess rsETH minted at the stale rate represents staking yield that belongs to existing rsETH holders but is instead captured by the attacker. This is a concrete, quantifiable **theft of unclaimed yield** (High severity). The daily mint limit bounds per-day loss but does not prevent it, and the attack is repeatable across multiple days and multiple destination chains.

## Likelihood Explanation
- `updateRate()` is permissionless; no privileged role is required to initiate a rate push.
- The attacker only needs to delay `lzReceive()` delivery on the destination chain, not compromise any key or oracle.
- Block stuffing on low-cost L2s is a documented, economically feasible attack.
- rsETH yield accrues continuously; any non-trivial delay between rate broadcasts creates a profitable window.
- No on-chain staleness check exists to revert or discount the deposit.

## Recommendation
1. **`CrossChainRateReceiver.getRate()`** — add a staleness guard: revert if `block.timestamp - lastUpdated > MAX_STALENESS` (e.g., 24 h).
2. **`RSETHPoolV3.viewSwapRsETHAmountAndFee()`** — read `lastUpdated` from the oracle interface and revert if stale before computing the mint amount.
3. **Oracle interface** — expose `lastUpdated` via `IOracle` so pool contracts can enforce freshness independently of the receiver implementation.

## Proof of Concept
```
1. Deploy RSETHPoolV3 pointing to a mock CrossChainRateReceiver
   initialized with rate = 1.00e18 (stale, pre-yield).
2. Simulate L1 rate increase to 1.01e18 (1% staking yield accrual)
   but do NOT call lzReceive on the receiver (simulates stuffed blocks
   or natural relay delay).
3. Attacker calls deposit() with 100 ETH:
   rsETH_stale  = 100e18 * 1e18 / 1.00e18 = 100.000e18
4. If rate were current:
   rsETH_current = 100e18 * 1e18 / 1.01e18 ≈  99.0099e18
5. Excess minted ≈ 0.9901 rsETH per 100 ETH (~1 ETH of stolen yield
   at 1.01 ETH/rsETH).
6. Assert rsETH_stale > rsETH_current — differential confirms
   invariant break.
```

Relevant code locations:
- [1](#0-0) 
- [2](#0-1) 
- [3](#0-2) 
- [4](#0-3) 
- [5](#0-4)

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L102-105)
```text
    /// @notice Gets the last stored rate in the contract
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L108-113)
```text
    function updateRate() external payable nonReentrant {
        uint256 latestRate = getLatestRate();

        rate = latestRate;

        lastUpdated = block.timestamp;
```

**File:** contracts/pools/RSETHPoolV3.sol (L96-125)
```text
    modifier limitDailyMint(uint256 amount, address token) {
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
        }

        uint256 rsETHAmount;

        // Calculate the amount of rsETH that will be minted
        if (token == ETH_IDENTIFIER) {
            (rsETHAmount,) = viewSwapRsETHAmountAndFee(amount);
        } else {
            (rsETHAmount,) = viewSwapRsETHAmountAndFee(amount, token);
        }

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
