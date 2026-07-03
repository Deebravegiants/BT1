### Title
L2 Pool `deposit` Functions Lack Minimum rsETH Output Protection (Slippage) - (File: contracts/pools/RSETHPoolNoWrapper.sol, contracts/pools/RSETHPoolV3.sol)

### Summary

The `deposit` functions across multiple L2 pool contracts mint rsETH/wrsETH to users based solely on the oracle rate at execution time, with no parameter allowing the caller to specify a minimum acceptable output. A user's ETH or LST input is consumed irreversibly, but the rsETH amount received can be silently lower than what the user simulated off-chain, with no revert path.

### Finding Description

The L2 pool contracts (`RSETHPoolNoWrapper`, `RSETHPoolV3`, `RSETHPool`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`) expose public `deposit` functions that compute the rsETH output as:

```
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate
```

where `rsETHToETHrate` is fetched live from the oracle at execution time. [1](#0-0) 

Neither the ETH-deposit variant nor the token-deposit variant accepts a `minRsETHAmountExpected` parameter: [2](#0-1) [3](#0-2) 

The same pattern is present in `RSETHPoolV3.deposit`: [4](#0-3) [5](#0-4) 

By contrast, the L1 `LRTDepositPool._beforeDeposit` explicitly enforces a caller-supplied minimum:

```solidity
if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
``` [6](#0-5) 

The L2 pool contracts have no equivalent guard. Once the user's ETH (or LST) is transferred in, the oracle rate at that block determines the rsETH minted, and the transaction succeeds regardless of how unfavorable the rate is.

### Impact Explanation

**Impact: Low — Contract fails to deliver promised returns without losing principal value.**

A user who previews `viewSwapRsETHAmountAndFee` off-chain and then submits a `deposit` transaction may receive materially fewer rsETH tokens than expected if the oracle rate is updated between preview and execution. The user's ETH is consumed and cannot be recovered; the rsETH received represents a smaller share of the protocol than the user intended to acquire. The voucher analog from the original report maps directly: the deposited ETH is "used up" (like the redeemed voucher), and the user has no on-chain mechanism to revert if the output falls below their acceptable threshold. [7](#0-6) 

### Likelihood Explanation

**Likelihood: Medium.**

The rsETH oracle rate is updated by an operator role and can change at any time. On L2 networks with public mempools (Arbitrum, Optimism, Base, Unichain), a pending `deposit` transaction is visible before inclusion. An oracle update that increases the rsETH/ETH rate (rsETH appreciates) will silently reduce the rsETH minted for any pending deposit. This is a normal operational event, not an attack, making it a recurring risk for every depositor who does not transact atomically with the oracle state. [8](#0-7) 

### Recommendation

Add a `minRsETHAmountExpected` parameter to each `deposit` function and revert if the computed `rsETHAmount` is below it, mirroring the protection already present in `LRTDepositPool._beforeDeposit`:

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

Apply the same pattern to the token-deposit overload and to all affected pool variants (`RSETHPoolV3`, `RSETHPool`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`). [9](#0-8) 

### Proof of Concept

1. Alice calls `viewSwapRsETHAmountAndFee(1 ether)` on `RSETHPoolNoWrapper` and sees she will receive `X` rsETH at the current oracle rate.
2. Alice submits `deposit{value: 1 ether}("ref")`.
3. Before Alice's transaction is included, the operator calls `setRSETHOracle` or the oracle itself updates, increasing the rsETH/ETH rate (rsETH is now worth more ETH per token).
4. Alice's transaction executes: `rsETHAmount = 1e18 * 1e18 / newHigherRate` — she receives fewer rsETH than `X`.
5. The transaction succeeds with no revert. Alice's 1 ETH is gone and she holds fewer rsETH than she expected, with no recourse. [2](#0-1) [1](#0-0)

### Citations

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L219-222)
```text
    /// @dev Gets the rate from the rsETHOracle
    function getRate() public view returns (uint256) {
        return IOracle(rsETHOracle).getRate();
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

**File:** contracts/LRTDepositPool.sol (L648-670)
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
    }
```
