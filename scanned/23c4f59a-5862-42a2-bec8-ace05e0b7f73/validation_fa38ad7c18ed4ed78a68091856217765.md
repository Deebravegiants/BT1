### Title
RSETHPool and RSETHPoolNoWrapper Missing Daily Mint Limit Allows Unrestricted Pool Draining - (File: contracts/pools/RSETHPool.sol, contracts/pools/RSETHPoolNoWrapper.sol)

### Summary
`RSETHPool` (Arbitrum) and `RSETHPoolNoWrapper` are missing the `dailyMintLimit` rate-limiting mechanism that is present in every other pool variant (`RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`). Any unprivileged depositor can drain the entire rsETH balance of these pools in a single transaction, temporarily freezing the deposit functionality for all other users.

### Finding Description
The protocol's pool contracts implement a `limitDailyMint` modifier that caps the total amount of rsETH that can be minted or transferred out of a pool within a 24-hour window. This mechanism is explicitly described as a safety control to prevent excessive exposure.

`RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, and `RSETHPoolV3WithNativeChainBridge` all apply `limitDailyMint` to every public `deposit` entry point:

```solidity
// RSETHPoolV3.sol – both deposit paths are guarded
function deposit(string memory referralId)
    external payable nonReentrant whenNotPaused
    limitDailyMint(msg.value, ETH_IDENTIFIER)   // ← rate limiter applied
{ ... }

function deposit(address token, uint256 amount, string memory referralId)
    external nonReentrant whenNotPaused onlySupportedToken(token)
    limitDailyMint(amount, token)               // ← rate limiter applied
{ ... }
``` [1](#0-0) [2](#0-1) 

By contrast, `RSETHPool` and `RSETHPoolNoWrapper` declare **no** `dailyMintLimit` state variable, **no** `limitDailyMint` modifier, and apply **no** rate-limiting check in either deposit path:

```solidity
// RSETHPool.sol – ETH deposit, no rate limiter
function deposit(string memory referralId)
    external payable nonReentrant whenNotPaused
{
    ...
    IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);
    ...
}

// RSETHPool.sol – token deposit, no rate limiter
function deposit(address token, uint256 amount, string memory referralId)
    external nonReentrant whenNotPaused onlySupportedToken(token)
{
    ...
    IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);
    ...
}
``` [3](#0-2) [4](#0-3) 

`RSETHPoolNoWrapper` has the identical omission:

```solidity
// RSETHPoolNoWrapper.sol – ETH deposit, no rate limiter
function deposit(string memory referralId)
    external payable nonReentrant whenNotPaused
{
    ...
    rsETH.safeTransfer(msg.sender, rsETHAmount);
    ...
}
``` [5](#0-4) [6](#0-5) 

Both contracts hold a pre-funded rsETH (or LZ_RSETH) balance that they transfer to depositors. Without a daily cap, a single depositor can exhaust the entire pool balance in one transaction.

### Impact Explanation
**Medium — Temporary freezing of funds.**

Once the pool's rsETH balance is exhausted, every subsequent `deposit` call reverts (insufficient balance), freezing the deposit functionality for all other users until the BRIDGER_ROLE replenishes the pool. The attacker pays fair-value ETH/tokens for the rsETH they receive, so this is not direct theft under normal oracle conditions; however, the safety cap that limits blast radius in any abnormal condition (e.g., a transient oracle discrepancy) is entirely absent. The daily limit in the guarded pools is explicitly sized to bound per-day exposure; its absence here removes that bound entirely.

### Likelihood Explanation
**Medium.** Any user holding sufficient ETH or a supported LST can trigger this in a single transaction with no special permissions. The Arbitrum (`RSETHPool`) and Unichain/no-wrapper (`RSETHPoolNoWrapper`) deployments are live production contracts with real rsETH balances. No front-running, governance capture, or privileged access is required.

### Recommendation
Add the same `dailyMintLimit` / `limitDailyMint` pattern used in `RSETHPoolV3` to both `RSETHPool` and `RSETHPoolNoWrapper`. Specifically:

1. Add `dailyMintLimit`, `dailyMintAmount`, `lastMintDay`, and `startTimestamp` state variables.
2. Implement the `limitDailyMint` modifier (identical to the one in `RSETHPoolV3`).
3. Apply the modifier to both `deposit(string)` and `deposit(address, uint256, string)` in each contract.
4. Add a `reinitializer` to set the initial limit and start timestamp, and a `setDailyMintLimit` admin function. [7](#0-6) 

### Proof of Concept
1. Observe that `RSETHPool` holds, say, 1 000 rsETH (LZ_RSETH) and the current oracle rate is `r` ETH/rsETH.
2. Attacker calls `RSETHPool.deposit{value: 1000 * r}("")`.
3. `viewSwapRsETHAmountAndFee` returns `~1000 rsETH` (minus fee).
4. `IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount)` succeeds, transferring the entire pool balance to the attacker.
5. All subsequent `deposit` calls by other users revert with an ERC-20 insufficient-balance error until the BRIDGER_ROLE manually replenishes the pool.
6. The same sequence applies to `RSETHPoolNoWrapper.deposit` on Unichain/Arbitrum.

No privileged access, no oracle manipulation, and no multi-step setup is required. [3](#0-2) [5](#0-4)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L50-125)
```text
    /// @notice The daily minting limit for rsETH
    uint256 public dailyMintLimit;

    /// @notice The amount of rsETH that was minted today
    uint256 public dailyMintAmount;

    /// @notice The last day that rsETH was minted
    uint256 public lastMintDay;

    /// @notice The start timestamp for the daily minting limit
    uint256 public startTimestamp;

    /// @notice The pauser role identifier
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");

    /// @notice The timelock role identifier
    bytes32 public constant TIMELOCK_ROLE = keccak256("TIMELOCK_ROLE");

    /// @notice The operator role identifier
    bytes32 public constant OPERATOR_ROLE = keccak256("OPERATOR_ROLE");

    modifier whenNotPaused() {
        if (paused) revert ContractPaused();
        _;
    }

    modifier whenPaused() {
        if (!paused) revert ContractNotPaused();
        _;
    }

    modifier onlySupportedToken(address token) {
        if (supportedTokenOracle[token] == address(0)) revert UnsupportedToken();
        _;
    }

    modifier onlySupportedTokenOrEth(address token) {
        if (token != ETH_IDENTIFIER && supportedTokenOracle[token] == address(0)) {
            revert UnsupportedToken();
        }
        _;
    }

    /// @dev Modifier to enforce the daily minting limit
    /// @param amount The asset amount sent in the deposit
    /// @param token The token address
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

**File:** contracts/pools/RSETHPool.sol (L284-305)
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

        IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId); // Add token address?
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
