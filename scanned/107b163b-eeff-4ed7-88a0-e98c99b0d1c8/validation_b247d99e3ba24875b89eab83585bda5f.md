### Title
No Slippage Control on `deposit` Functions Across L2 Pool Contracts - (File: contracts/pools/RSETHPool.sol, RSETHPoolNoWrapper.sol, RSETHPoolV2.sol, RSETHPoolV3.sol)

### Summary
All L2 pool `deposit` functions lack a `minRsETHAmount` parameter, exposing depositors to receiving fewer rsETH than expected when the oracle rate changes between transaction submission and execution. This is the direct analog of the `IbbtcVaultZap.sol` finding: `LRTDepositPool.sol` correctly implements `minRSETHAmountExpected`, but none of the L2 pool contracts do.

### Finding Description
Every L2 pool contract exposes public `deposit` functions that compute the rsETH output amount solely from the oracle rate at execution time, with no caller-supplied minimum:

- `RSETHPool.sol` `deposit(string)` (ETH) and `deposit(address,uint256,string)` (token)
- `RSETHPoolNoWrapper.sol` `deposit(string)` and `deposit(address,uint256,string)`
- `RSETHPoolV2.sol` `deposit(string)`
- `RSETHPoolV3.sol` `deposit(string)` and `deposit(address,uint256,string)`

In each case the rsETH amount is computed as:

```
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate   // ETH path
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate  // token path
```

where `rsETHToETHrate` is read from `rsETHOracle` at execution time. There is no check of the form `if (rsETHAmount < minRsETHAmount) revert`. The user has no on-chain mechanism to bound the minimum rsETH they will receive.

By contrast, `LRTDepositPool.sol` (the L1 deposit contract) correctly enforces:

```solidity
if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
```

The L2 pool contracts are missing this protection entirely.

### Impact Explanation
**Low — Contract fails to deliver promised returns, but doesn't lose value.**

A user who previews the swap off-chain via `viewSwapRsETHAmountAndFee` and then submits a `deposit` transaction may receive materially fewer rsETH than previewed if the oracle rate increases (rsETH appreciates) between submission and execution. The user's ETH/token is consumed but the rsETH minted is less than the user intended to accept. No ETH is stolen by an attacker, but the user suffers an uncontrolled loss of rsETH value relative to their expectation. On congested L2 sequencers or during periods of rapid rsETH rate appreciation, the gap can be significant.

### Likelihood Explanation
**Medium.** The rsETH/ETH rate increases continuously as staking rewards accrue. Any deposit transaction that sits in the mempool or is delayed by the sequencer executes at a worse rate than previewed. No attacker action is required — natural rate drift is sufficient. On L2s with sequencer reordering, the risk is further elevated.

### Recommendation
Add a `minRsETHAmountExpected` parameter to every public `deposit` function in all L2 pool contracts, mirroring the pattern already used in `LRTDepositPool.sol`:

```solidity
function deposit(string memory referralId, uint256 minRsETHAmountExpected)
    external payable nonReentrant whenNotPaused
{
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minRsETHAmountExpected) revert MinimumAmountToReceiveNotMet();
    ...
}
```

Apply the same pattern to the token-deposit overloads.

### Proof of Concept

**`RSETHPool.sol` ETH deposit — no minimum check:** [1](#0-0) 

**`RSETHPool.sol` token deposit — no minimum check:** [2](#0-1) 

**`RSETHPoolNoWrapper.sol` ETH deposit — no minimum check:** [3](#0-2) 

**`RSETHPoolV2.sol` deposit — no minimum check:** [4](#0-3) 

**`RSETHPoolV3.sol` ETH deposit — no minimum check:** [5](#0-4) 

**`LRTDepositPool.sol` — correct pattern with `minRSETHAmountExpected` (reference):** [6](#0-5)

### Citations

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

**File:** contracts/pools/RSETHPoolV2.sol (L207-219)
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

**File:** contracts/LRTDepositPool.sol (L648-669)
```text
    function _beforeDeposit(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected
    )
        private
        view
        returns (uint256 rsethAmountToMint)
    {
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
```
