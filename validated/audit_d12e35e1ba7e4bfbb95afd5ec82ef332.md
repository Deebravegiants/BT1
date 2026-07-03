### Title
Missing Daily Mint Limit in RSETHPoolNoWrapper Allows Unlimited Swaps Per Day — (File: contracts/pools/RSETHPoolNoWrapper.sol)

### Summary

`RSETHPoolNoWrapper` is the only L2 deposit pool variant that lacks a daily swap/distribution limit. Every other pool variant enforces a `limitDailyMint` modifier on its `deposit()` functions. Any unprivileged depositor can call `RSETHPoolNoWrapper.deposit()` with an arbitrarily large amount, bypassing the intended daily cap and draining the pool's entire rsETH balance in a single transaction.

### Finding Description

All three sibling pool contracts enforce a `limitDailyMint` modifier on every `deposit()` entry point:

- `RSETHPoolV3.deposit()` — `limitDailyMint(amount, token)` [1](#0-0) 
- `RSETHPoolV3ExternalBridge.deposit()` — `limitDailyMint(amount, token)` [2](#0-1) 
- `RSETHPoolV3WithNativeChainBridge.deposit()` — `limitDailyMint(amount, token)` [3](#0-2) 

`RSETHPoolNoWrapper`, however, declares neither a `dailyMintLimit` state variable nor a `limitDailyMint` modifier. Both of its public `deposit()` functions are guarded only by `nonReentrant` and `whenNotPaused`:

```solidity
function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
    ...
    rsETH.safeTransfer(msg.sender, rsETHAmount);
}

function deposit(address token, uint256 amount, string memory referralId)
    external nonReentrant whenNotPaused onlySupportedToken(token)
{
    ...
    rsETH.safeTransfer(msg.sender, rsETHAmount);
}
``` [4](#0-3) 

There is no `dailyMintLimit` field anywhere in the contract. [5](#0-4) 

The design intent for a daily cap is unambiguous: every other pool variant stores `dailyMintLimit`, `dailyMintAmount`, and `lastMintDay`, and the admin setter `setDailyMintLimit()` is present in all of them. The absence of these controls in `RSETHPoolNoWrapper` is an omission, not a deliberate design choice, because the same risk-management rationale (limiting daily rsETH outflow) applies regardless of whether the pool mints new wrapper tokens or transfers canonical rsETH.

### Impact Explanation

**Low — Contract fails to deliver promised returns, but doesn't lose value.**

A depositor can swap an arbitrarily large amount of ETH or supported LSTs for rsETH in a single transaction, draining the pool's entire rsETH balance. After the drain, subsequent users cannot swap until the pool is refilled by the bridger. No funds are stolen (the depositor pays fair market value), but the protocol's intended daily distribution cap is completely unenforced, and other users are temporarily unable to use the pool.

### Likelihood Explanation

**High.** The entry path is fully permissionless — any externally owned account can call `deposit()` with `msg.value` equal to the pool's entire ETH-equivalent rsETH balance. No special role, flash loan, or multi-step setup is required.

### Recommendation

Add `dailyMintLimit`, `dailyMintAmount`, `lastMintDay`, and `startTimestamp` state variables to `RSETHPoolNoWrapper`, implement a `limitDailyMint` modifier identical to the one in the sibling contracts, and apply it to both `deposit()` overloads. Provide a `setDailyMintLimit()` admin function and a `reinitialize()` entry point to configure the limit, mirroring the pattern in `RSETHPoolV3`.

### Proof of Concept

1. Deploy `RSETHPoolNoWrapper` on Arbitrum (or Unichain) with a pre-funded rsETH balance of, say, 10 000 rsETH.
2. Call `deposit{value: X}("")` where `X` is chosen so that `viewSwapRsETHAmountAndFee(X).rsETHAmount` equals the full 10 000 rsETH balance.
3. The call succeeds with no daily-limit check; the caller receives all 10 000 rsETH in one transaction.
4. All subsequent callers receive `TransferFailed` (or an ERC-20 insufficient-balance revert) until the pool is refilled.
5. Repeat the same call on any sibling pool (`RSETHPoolV3`, etc.) — it reverts with `DailyMintLimitExceeded`, confirming the protection is present there but absent in `RSETHPoolNoWrapper`.

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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L130-158)
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
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L108-136)
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
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L33-84)
```text
    /// @notice Roles
    bytes32 public constant BRIDGER_ROLE = keccak256("BRIDGER_ROLE");
    bytes32 public constant TIMELOCK_ROLE = keccak256("TIMELOCK_ROLE");

    /// @notice The canonical rsETH token address (rsETH OFT)
    IERC20 public rsETH;

    /// @notice Basis points for fees
    uint256 public feeBps;

    /// @notice Fee earned in ETH
    uint256 public feeEarnedInETH;

    /// @notice The rsETHOracle address
    address public rsETHOracle;

    /// @notice Flag to enable/disable native ETH deposits
    bool public isEthDepositEnabled;

    /// @notice Mapping to track fees earned in different tokens
    mapping(address token => uint256 feeEarned) public feeEarnedInToken;

    /// @notice Mapping of supported tokens to their oracles
    mapping(address token => address oracle) public supportedTokenOracle;

    /// @notice Array of supported tokens
    address[] public supportedTokenList;

    /// @notice The corresponding L1Vault contract for the L2 chain
    address public l1VaultETHForL2Chain;

    /// @notice The StargatePool used for L2 --> L1 bridging
    IStargatePoolNative public stargatePool;

    /// @notice The LayerZero ID for the ETH mainnet
    uint32 public dstLzChainId;

    /// @notice The latest transaction receipt info from the StargatePoolNative
    TxReceipt public latestTxReceipt;

    /// @notice The mapping of token addresses to their respective token bridges
    mapping(address token => address bridge) public tokenBridge;

    /// @notice The address of the L2 bridge contract on Unichain
    address public l2Bridge;

    /// @notice The address of the Unichain messenger contract
    address public messenger;

    /// @notice The pauser role identifier
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");

```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L231-271)
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

    /// @dev Swaps token for rsETH
    /// @param token The token address
    /// @param amount The amount of token
    /// @param referralId The referral id
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
