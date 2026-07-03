### Title
Deposit output amount rounds down to zero with no guard, permanently locking depositor funds — (`contracts/pools/RSETHPool.sol`, `contracts/pools/RSETHPoolNoWrapper.sol`, `contracts/pools/RSETHPoolV3.sol`, `contracts/agETH/AGETHPoolV3.sol`)

---

### Summary

Every public `deposit` function across the pool family computes the output amount (`rsETHAmount` / `agETHAmount`) with a plain integer division that can silently produce zero. When it does, the depositor's ETH or ERC-20 tokens are accepted by the contract and permanently locked, while the depositor receives nothing in return. No guard exists to reject a zero-output deposit.

---

### Finding Description

All pool contracts share the same output-amount formula. For ETH deposits:

```solidity
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

For token deposits:

```solidity
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

Because `rsETHToETHrate` is always greater than `1e18` (rsETH accrues value over time), any ETH deposit where `amountAfterFee < rsETHToETHrate / 1e18` (i.e., a few wei) produces `rsETHAmount = 0`. The same truncation applies to token deposits when `amountAfterFee * tokenToETHRate < rsETHToETHrate`.

The deposit functions only guard against a zero *input*:

```solidity
if (amount == 0) revert InvalidAmount();
```

There is no corresponding guard on the *output*. The flow then proceeds unconditionally:

- `RSETHPool.sol` / `RSETHPoolNoWrapper.sol`: `rsETH.safeTransfer(msg.sender, rsETHAmount)` — transfers 0 tokens silently.
- `RSETHPoolV3.sol` / `AGETHPoolV3.sol`: `wrsETH.mint(msg.sender, rsETHAmount)` — mints 0 tokens silently.

The deposited ETH or ERC-20 tokens are now held by the pool, counted as part of the bridgeable balance, and will eventually be bridged to L1 — with no record of the depositor's claim.

The same pattern is present in every pool variant: [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7) 

---

### Impact Explanation

**Low — Contract fails to deliver promised returns.**

A depositor who sends a dust ETH amount (e.g., 1 wei) or a very small token amount receives 0 rsETH/agETH. Their deposited assets are absorbed into the pool's bridgeable balance and bridged to L1 with no depositor claim attached. The depositor has no recovery path. The protocol itself does not lose funds, but the depositor does.

---

### Likelihood Explanation

**Low.** For the currently supported 18-decimal ETH-correlated LSTs, the threshold at which `rsETHAmount` truncates to zero is a few wei of ETH — amounts no rational user would intentionally deposit. However:

1. The `addSupportedToken` function imposes no restriction on token decimals. If a 6-decimal token (e.g., USDC) is added, the truncation threshold rises to roughly `rsETHToETHrate / tokenToETHRate` units of that token — potentially several thousand base units (thousandths of a dollar), making accidental zero-output deposits realistic.
2. A malicious actor could grief a specific depositor by front-running their transaction with a tiny deposit that shifts the rate just enough to push the victim's output to zero — though this is a marginal scenario given the current token set. [9](#0-8) 

---

### Recommendation

Add an output-amount guard immediately after computing `rsETHAmount` / `agETHAmount` in every deposit function:

```solidity
if (rsETHAmount == 0) revert InvalidAmount();
```

This mirrors the fix applied in the referenced PuttyV2 report and is consistent with the zero-amount guard already present on the input side. Apply the same guard in `viewSwapRsETHAmountAndFee` / `viewSwapAgETHAmountAndFee` so callers can detect the condition off-chain before submitting a transaction.

---

### Proof of Concept

**ETH deposit path (`RSETHPool.sol`):**

1. `rsETHToETHrate` = `1.05e18` (rsETH has accrued 5% above peg).
2. Depositor calls `deposit{value: 1}("")` (1 wei ETH).
3. `viewSwapRsETHAmountAndFee(1)`:
   - `fee = 1 * feeBps / 10_000 = 0`
   - `amountAfterFee = 1`
   - `rsETHAmount = 1 * 1e18 / 1.05e18 = 0` (integer truncation)
4. `feeEarnedInETH += 0`.
5. `IERC20(address(wrsETH)).safeTransfer(msg.sender, 0)` — succeeds silently.
6. Depositor's 1 wei is now in the pool's ETH balance, counted as bridgeable, and will be sent to L1. Depositor holds no rsETH and has no claim. [1](#0-0) [2](#0-1)

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

**File:** contracts/pools/RSETHPool.sol (L637-656)
```text
    function addSupportedToken(address token, address oracle, address bridge) external onlyRole(TIMELOCK_ROLE) {
        UtilLib.checkNonZeroAddress(token);
        UtilLib.checkNonZeroAddress(oracle);
        UtilLib.checkNonZeroAddress(bridge);

        if (supportedTokenOracle[token] != address(0)) {
            revert AlreadySupportedToken();
        }
        if (tokenBridge[token] != address(0)) {
            revert AlreadySupportedToken();
        }
        if (IOracle(oracle).getRate() == 0) {
            revert UnsupportedOracle();
        }
        supportedTokenList.push(token);
        supportedTokenOracle[token] = oracle;
        tokenBridge[token] = bridge;

        emit AddSupportedToken(token, oracle, bridge);
    }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L231-243)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        rsETH.safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L277-285)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolV3.sol (L244-265)
```text
    /// @dev Swaps ETH for rsETH
    /// @param referralId The referral id
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

**File:** contracts/pools/RSETHPoolV3.sol (L299-307)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

**File:** contracts/agETH/AGETHPoolV3.sol (L115-128)
```text
    function deposit(string memory referralId) external payable nonReentrant {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 agETHAmount, uint256 fee) = viewSwapAgETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        agETH.mint(msg.sender, agETHAmount);

        emit SwapOccurred(msg.sender, agETHAmount, fee, referralId);
    }
```

**File:** contracts/agETH/AGETHPoolV3.sol (L160-168)
```text
    function viewSwapAgETHAmountAndFee(uint256 amount) public view returns (uint256 agETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of agETH in ETH
        uint256 agETHToETHrate = getRate();

        // Calculate the final agETH amount
        agETHAmount = amountAfterFee * 1e18 / agETHToETHrate;
```
