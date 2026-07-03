### Title
Missing Daily Mint Rate Limit in RSETHPool and RSETHPoolNoWrapper Allows Pool rsETH Drainage - (File: contracts/pools/RSETHPool.sol, contracts/pools/RSETHPoolNoWrapper.sol)

### Summary
`RSETHPool.sol` and `RSETHPoolNoWrapper.sol` are the only pool variants in the protocol that lack the `limitDailyMint` rate-limiting modifier present in every other pool variant. Any unprivileged depositor with sufficient ETH or LST can drain the entire rsETH balance of these pools in a single transaction, temporarily preventing all other users from depositing until the BRIDGER_ROLE manually refills the pool.

### Finding Description
All newer pool variants — `RSETHPoolV3`, `RSETHPoolV2ExternalBridge`, `RSETHPoolV3ExternalBridge`, and `RSETHPoolV3WithNativeChainBridge` — implement a `limitDailyMint` modifier that caps the total rsETH minted or distributed per day: [1](#0-0) 

This modifier resets a daily counter and enforces `dailyMintAmount + rsETHAmount <= dailyMintLimit` before any deposit proceeds.

`RSETHPool.sol` (Arbitrum) and `RSETHPoolNoWrapper.sol` have no such guard. Their `deposit` functions are: [2](#0-1) [3](#0-2) 

Both functions transfer rsETH directly from the pool's own balance to the caller with no per-day cap. The only guards are `nonReentrant`, `whenNotPaused`, and `isEthDepositEnabled` — none of which limit the volume per day.

### Impact Explanation
These pools hold a finite pre-funded rsETH balance (LZ_RSETH on Arbitrum; canonical rsETH OFT on Unichain). A single depositor can submit one transaction depositing enough ETH/LST to receive the entire rsETH balance of the pool. Once drained, every subsequent `deposit` call from any other user reverts with an ERC-20 insufficient-balance error. The pool remains non-functional for all depositors until the BRIDGER_ROLE bridges new rsETH back to the pool — a manual, off-chain-triggered operation with no guaranteed SLA. This constitutes a **temporary freezing of the deposit service** for all L2 users of these pools.

**Impact: Medium — Temporary freezing of funds.**

### Likelihood Explanation
The attack requires no special role, no oracle manipulation, and no governance action. Any address with sufficient ETH or a supported LST can execute it in a single transaction. The attacker receives fair-value rsETH in return (no capital loss), making this a low-cost griefing vector. The only friction is the capital required to drain the pool, which scales with pool size.

**Likelihood: Medium.**

### Recommendation
Add the `limitDailyMint` modifier (or an equivalent daily cap mechanism) to both `deposit` overloads in `RSETHPool.sol` and `RSETHPoolNoWrapper.sol`, consistent with the pattern already implemented in all other pool variants: [4](#0-3) [5](#0-4) 

The `dailyMintLimit` and `startTimestamp` state variables, along with the `setDailyMintLimit` admin function and `reinitialize` upgrade path, should be added to both contracts following the same pattern.

### Proof of Concept
1. Attacker queries the rsETH balance of `RSETHPool` (Arbitrum) or `RSETHPoolNoWrapper` (Unichain).
2. Attacker calls `deposit{value: X}("")` where `X` is large enough that `viewSwapRsETHAmountAndFee(X).rsETHAmount` equals or exceeds the pool's rsETH balance.
3. The pool executes `IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount)` — transferring all available rsETH to the attacker.
4. All subsequent `deposit` calls from other users revert because `rsETH.balanceOf(pool) == 0`.
5. The pool is non-functional until the BRIDGER_ROLE manually refills it via the L1→L2 bridging pipeline. [2](#0-1) [3](#0-2)

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

**File:** contracts/pools/RSETHPoolV3.sol (L271-293)
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
        limitDailyMint(amount, token)
    {
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
    }
```

**File:** contracts/pools/RSETHPool.sol (L265-278)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);

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
