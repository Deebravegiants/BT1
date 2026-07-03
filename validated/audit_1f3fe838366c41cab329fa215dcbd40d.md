Audit Report

## Title
Missing `minRsETHAmount` Slippage Guard in L2 Pool Deposit Functions — (File: contracts/pools/RSETHPoolV3.sol)

## Summary
All L2 pool `deposit` entry points (`RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, `RSETHPoolNoWrapper`) compute the rsETH mint amount from a live oracle rate and immediately mint, with no user-supplied minimum output floor. The mainnet `LRTDepositPool` correctly enforces this guard via `minRSETHAmountExpected`. Any depositor whose transaction is pending during a routine oracle rate update receives fewer rsETH than they observed off-chain, with no on-chain recourse.

## Finding Description
`LRTDepositPool.depositETH` accepts `minRSETHAmountExpected` and passes it to `_beforeDeposit`, which reverts with `MinimumAmountToReceiveNotMet` if `rsethAmountToMint < minRSETHAmountExpected` (lines 667–669). [1](#0-0) 

By contrast, `RSETHPoolV3.deposit(string memory referralId)` (lines 246–265) and `RSETHPoolV3.deposit(address token, uint256 amount, string memory referralId)` (lines 271–293) call `viewSwapRsETHAmountAndFee`, which divides `amountAfterFee * 1e18` by the live `getRate()` return value, and immediately mint — no floor check exists. [2](#0-1) [3](#0-2) 

The same omission is present in `RSETHPoolV3ExternalBridge.deposit` (lines 366–384) and `RSETHPoolNoWrapper.deposit` (lines 231–271). [4](#0-3) [5](#0-4) 

Exploit path:
1. Alice calls `viewSwapRsETHAmountAndFee(1 ether)` off-chain and observes she will receive `X` wrsETH.
2. Alice submits `RSETHPoolV3.deposit{value: 1 ether}("ref")`.
3. Before Alice's transaction is mined, the oracle rate is updated (reward accrual), increasing `rsETHToETHrate`.
4. Alice's transaction executes: `rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate` is now smaller than `X`.
5. Alice receives fewer wrsETH than expected with no on-chain protection.

No adversarial action is required; routine reward accrual oracle updates are sufficient.

## Impact Explanation
**Low — Contract fails to deliver promised returns, but doesn't lose value.**

The deposited ETH/LST is correctly accounted for in the protocol. However, the user's rsETH share is silently reduced relative to their expectation at transaction submission time, with no mechanism to revert. This matches the allowed Low impact: "Contract fails to deliver promised returns, but doesn't lose value."

## Likelihood Explanation
The rsETH oracle rate is updated regularly as staking rewards accrue on mainnet and are reflected on L2. Any deposit transaction pending in the mempool during such an update is silently subject to a worse rate. No privileged access, adversarial actor, or external protocol compromise is required — normal protocol operation triggers the condition. L2 mempools with public visibility make the timing observable.

## Recommendation
Add a `uint256 minRsETHAmount` parameter to every L2 pool `deposit` function, mirroring the pattern in `LRTDepositPool._beforeDeposit`:

```solidity
function deposit(string memory referralId, uint256 minRsETHAmount) external payable ... {
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minRsETHAmount) revert SlippageExceeded();
    wrsETH.mint(msg.sender, rsETHAmount);
}
```

Apply the same change to the token-deposit overload and to all pool variants (`RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, `RSETHPoolNoWrapper`). [6](#0-5) 

## Proof of Concept
Foundry fork test plan:
1. Fork the target L2 at a block where `getRate()` returns `R`.
2. Call `RSETHPoolV3.viewSwapRsETHAmountAndFee(1 ether)` → record `expectedRsETH`.
3. Warp/prank the oracle to update `getRate()` to `R * 1.001` (simulating a reward accrual update).
4. Call `RSETHPoolV3.deposit{value: 1 ether}("ref")` from Alice's address.
5. Assert `wrsETH.balanceOf(alice) < expectedRsETH` — the transaction succeeds silently with a reduced output.
6. Confirm that the equivalent call on `LRTDepositPool.depositETH` with `minRSETHAmountExpected = expectedRsETH` reverts with `MinimumAmountToReceiveNotMet`. [7](#0-6)

### Citations

**File:** contracts/LRTDepositPool.sol (L76-93)
```text
    function depositETH(
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        payable
        nonReentrant
        whenNotPaused
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L665-669)
```text
        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
```

**File:** contracts/pools/RSETHPoolV3.sol (L258-262)
```text
        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L366-384)
```text
    function deposit(string memory referralId)
        external
        payable
        nonReentrant
        whenNotPaused
        limitDailyMint(msg.value, ETH_IDENTIFIER)
    {
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
