### Title
Depositors Cannot Specify Minimum wrsETH Output in L2 Pool Deposits, Lacking Slippage Protection - (File: contracts/pools/RSETHPoolV3.sol)

### Summary

All L2 pool `deposit()` functions (`RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, `RSETHPoolNoWrapper`) compute the minted wrsETH/rsETH amount solely from the oracle rate at execution time, with no caller-supplied minimum-output guard. The L1 counterpart (`LRTDepositPool`) already accepts a `minRSETHAmountExpected` parameter, proving the protocol recognises the need — but the L2 pools omit it entirely.

### Finding Description

Every L2 pool deposit function resolves the output amount at execution time by calling `getRate()`:

```solidity
// RSETHPoolV3.sol L258-262
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
// ...
wrsETH.mint(msg.sender, rsETHAmount);
```

`viewSwapRsETHAmountAndFee` divides by the live oracle rate:

```solidity
// RSETHPoolV3.sol L304-307
uint256 rsETHToETHrate = getRate();
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

The depositor supplies only `referralId`; there is no `minRsETHAmountExpected` argument. If the oracle rate rises between the moment the user signs the transaction and the moment it is included in a block, the user receives fewer wrsETH than anticipated, with no on-chain protection and no ability to cancel.

By contrast, the L1 deposit pool enforces an explicit lower bound:

```solidity
// LRTDepositPool.sol L667-669
rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);
if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
```

The same gap exists in `RSETHPoolV3ExternalBridge.deposit()`, `RSETHPoolV3WithNativeChainBridge.deposit()`, and `RSETHPoolNoWrapper.deposit()`.

### Impact Explanation

A depositor who observes a favourable rate off-chain and submits a transaction may receive materially fewer wrsETH/rsETH than expected if the oracle is updated in the same block or a subsequent block before their transaction settles. Because the ETH/LST is immediately transferred to the pool and bridged to L1, the user has no recourse. The contract fails to deliver the output the user reasonably expected at submission time.

**Impact: Low** — Contract fails to deliver promised returns, but does not lose the deposited value outright.

### Likelihood Explanation

The `rsETHOracle` rate is updated periodically to reflect accrued staking rewards. On L2 chains, block times are short and mempool ordering is less predictable than on L1. Any oracle update that lands before a pending deposit transaction will silently reduce the user's output. This is a routine operational event, not an exotic attack, making it a realistic and recurring condition.

### Recommendation

Add a `minRsETHAmountExpected` parameter to all L2 pool `deposit()` overloads and revert if the computed output falls below it, mirroring the pattern already used in `LRTDepositPool`:

```solidity
function deposit(string memory referralId, uint256 minRsETHAmountExpected)
    external payable nonReentrant whenNotPaused
    limitDailyMint(msg.value, ETH_IDENTIFIER)
{
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minRsETHAmountExpected) revert SlippageExceeded();
    wrsETH.mint(msg.sender, rsETHAmount);
}
```

Apply the same change to the token-deposit overload and to `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, and `RSETHPoolNoWrapper`.

### Proof of Concept

1. Oracle rate is `1.05e18` (1 ETH = ~0.952 wrsETH). User submits `deposit{value: 1 ether}("ref")` expecting ≈0.952 wrsETH.
2. Before the transaction is mined, the oracle is updated to `1.10e18`.
3. Transaction executes: `rsETHAmount = 1e18 * 1e18 / 1.10e18 ≈ 0.909e18` — the user receives ~4.5% fewer tokens than expected with no revert and no recourse.
4. The L1 path (`LRTDepositPool.depositETH(minRSETHAmountExpected)`) would have reverted at step 3, protecting the user.

---

**Affected locations:**

- `deposit(string)` and `deposit(address,uint256,string)` in `RSETHPoolV3` [1](#0-0) 
- `viewSwapRsETHAmountAndFee` computing output from live oracle with no floor [2](#0-1) 
- Same pattern in `RSETHPoolV3ExternalBridge.deposit()` [3](#0-2) 
- Same pattern in `RSETHPoolV3WithNativeChainBridge.deposit()` [4](#0-3) 
- Same pattern in `RSETHPoolNoWrapper.deposit()` [5](#0-4) 
- L1 reference implementation with correct slippage guard [6](#0-5)

### Citations

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

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L282-301)
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

**File:** contracts/LRTDepositPool.sol (L665-669)
```text
        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
```
