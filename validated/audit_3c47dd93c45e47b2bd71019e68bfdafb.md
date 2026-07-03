### Title
Missing Daily Mint Limit in `RSETHPoolNoWrapper` Allows Unbounded rsETH Drain on Oracle Failure - (File: contracts/pools/RSETHPoolNoWrapper.sol)

### Summary
`RSETHPoolNoWrapper` is the deposit pool for chains without a local rsETH wrapper (e.g., Arbitrum, Unichain). Unlike its sibling contracts `RSETHPoolV3` and `RSETHPoolV3ExternalBridge`, it has no daily mint/dispense limit. If the oracle returns a manipulated or temporarily incorrect rate, an attacker can drain the entire rsETH balance held by the pool in a single transaction, with no circuit breaker to limit the damage.

### Finding Description
`RSETHPoolV3` and `RSETHPoolV3ExternalBridge` both implement a `limitDailyMint` modifier that caps the total rsETH dispensed per 24-hour window: [1](#0-0) 

Both sibling contracts apply this modifier on every `deposit()` call: [2](#0-1) 

`RSETHPoolNoWrapper`, however, has no such limit. Its `deposit()` functions are gated only by `whenNotPaused` and `nonReentrant`: [3](#0-2) [4](#0-3) 

The rsETH amount dispensed is computed as: [5](#0-4) 

`rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate`. If `rsETHToETHrate` is temporarily incorrect (e.g., returns a near-zero value due to oracle failure or manipulation), `rsETHAmount` becomes astronomically large. Unlike `RSETHPoolV3` which mints new wrsETH, `RSETHPoolNoWrapper` transfers rsETH directly from its own pre-funded balance: [6](#0-5) 

There is no per-day cap, no per-transaction cap, and no global limit on how much rsETH can be transferred out. The entire pool balance can be drained in a single call.

### Impact Explanation
**Critical — Direct theft of rsETH tokens held in the pool.**

The pool holds a pre-funded rsETH balance. An oracle failure or manipulation causes `getRate()` to return a value far below the true rate. An attacker deposits a negligible amount of ETH or a supported LST and receives the entire rsETH balance of the pool. The attacker then holds rsETH worth far more than what was deposited, constituting direct theft of protocol-held funds. Because there is no daily limit, the full balance is at risk in a single block.

### Likelihood Explanation
**Medium.** The oracle (`rsETHOracle`) is an external contract whose address is set by `TIMELOCK_ROLE`. A temporary oracle failure (stale feed, price spike, or a bug in the oracle contract) is a realistic scenario explicitly described in the external report. The `RSETHPoolNoWrapper` is deployed on chains where the oracle is a cross-chain rate provider, making it more susceptible to transient rate anomalies than a local Chainlink feed. No privileged access is required by the attacker — only a public `deposit()` call.

### Recommendation
Add the same `dailyMintLimit` / `limitDailyMint` mechanism present in `RSETHPoolV3` and `RSETHPoolV3ExternalBridge` to `RSETHPoolNoWrapper`. Specifically:

1. Add state variables `dailyMintLimit`, `dailyMintAmount`, `lastMintDay`, and `startTimestamp`.
2. Implement a `limitDailyMint(uint256 amount)` modifier that computes the rsETH equivalent of the deposited amount and reverts if the daily cap would be exceeded.
3. Apply this modifier to both `deposit(string)` and `deposit(address, uint256, string)`.
4. Add a `setDailyMintLimit()` admin function and a `reinitialize()` to set the initial limit.

### Proof of Concept
1. The oracle at `rsETHOracle` temporarily returns `getRate() = 1` (1 wei) instead of the correct ~1.05e18.
2. Attacker calls `RSETHPoolNoWrapper.deposit{value: 1 ether}("ref")`.
3. `viewSwapRsETHAmountAndFee(1 ether)` computes:
   - `fee = 1 ether * feeBps / 10_000` (small)
   - `amountAfterFee ≈ 1 ether`
   - `rsETHAmount = 1e18 * 1e18 / 1 = 1e36` rsETH
4. `rsETH.safeTransfer(attacker, 1e36)` — the pool's entire rsETH balance is transferred to the attacker (capped by the pool's actual balance).
5. No daily limit check exists to prevent or bound this transfer.
6. The attacker holds rsETH worth orders of magnitude more than the 1 ETH deposited. The pool is fully drained in a single transaction.

### Citations

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

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L231-244)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        rsETH.safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L250-271)
```text
    function deposit(
        address token,
        uint256 amount,
        string memory referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedToken(token)
    {
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        rsETH.safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId); // Add token address?
    }
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
