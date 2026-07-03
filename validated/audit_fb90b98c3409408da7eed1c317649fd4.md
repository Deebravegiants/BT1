### Title
`deposit` Functions in RSETHPool Contracts Lack Slippage Protection, Allowing Users to Receive Fewer rsETH Than Expected - (File: contracts/pools/RSETHPool.sol, RSETHPoolNoWrapper.sol, RSETHPoolV3.sol, RSETHPoolV3ExternalBridge.sol, RSETHPoolV3WithNativeChainBridge.sol)

---

### Summary

All L2 pool `deposit` functions (ETH and token variants) compute the rsETH output amount at execution time by reading a live oracle rate, but accept no `minRSETHAmountExpected` parameter. A user whose transaction is delayed in the mempool or executed after an oracle rate update will silently receive fewer rsETH tokens than they anticipated when they signed the transaction, with no on-chain protection.

---

### Finding Description

Every pool contract exposes two public `deposit` entry points — one for native ETH and one for ERC-20 tokens — that are callable by any unprivileged user:

**RSETHPool.sol (ETH path):** [1](#0-0) 

**RSETHPool.sol (token path):** [2](#0-1) 

In both cases the rsETH output is determined entirely by `viewSwapRsETHAmountAndFee`, which reads the live oracle rate at execution time: [3](#0-2) 

The same pattern is present in every other pool variant: [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) 

None of these functions accept a caller-supplied minimum output amount. The user has no way to bound the worst-case rsETH they will receive.

By contrast, the L1 `LRTDepositPool` correctly implements slippage protection via a `minRSETHAmountExpected` parameter that is enforced inside `_beforeDeposit`: [8](#0-7) [9](#0-8) 

The pool contracts are the only deposit path that omits this guard.

---

### Impact Explanation

A user submits a `deposit` transaction quoting a rate of, say, 1.05 ETH per rsETH. Before the transaction is mined, the oracle is updated to 1.10 ETH per rsETH (rsETH appreciated). The user's transaction executes at the new rate and they receive ~4.5 % fewer rsETH than they expected, with no revert and no recourse. The deposited ETH is fully consumed; the shortfall accrues to the pool's rsETH reserve rather than to the user. This constitutes a silent failure to deliver the promised return.

**Impact: Low — Contract fails to deliver promised returns, but does not lose principal value.**

---

### Likelihood Explanation

The rsETH oracle rate is updated by the protocol whenever the underlying LST basket accrues yield or rebalances. On active chains this can happen multiple times per day. Any transaction that sits in the mempool across an oracle update — due to low gas, network congestion, or deliberate delay — will execute at the new, less favorable rate. No adversarial action is required; ordinary mempool latency is sufficient. The affected entry points are public and used by every depositor on every supported L2 chain.

**Likelihood: Medium** — oracle updates are routine and mempool delays are common.

---

### Recommendation

Add a `minRSETHAmountExpected` parameter to every `deposit` overload in all pool contracts, mirroring the pattern already used in `LRTDepositPool`:

```solidity
function deposit(string memory referralId, uint256 minRSETHAmountExpected)
    external payable nonReentrant whenNotPaused
{
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minRSETHAmountExpected) revert SlippageExceeded();
    ...
}
```

Apply the same guard to the ERC-20 token `deposit` overload and to all pool variants (`RSETHPoolNoWrapper`, `RSETHPoolV2`, `RSETHPoolV2NBA`, `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`).

---

### Proof of Concept

1. Oracle reports `rsETHToETHrate = 1.05e18` (1 rsETH = 1.05 ETH).
2. User calls `RSETHPool.deposit{value: 1.05 ether}("ref")` expecting to receive `1e18` rsETH (minus fee).
3. Transaction sits in the mempool. Protocol updates the oracle to `rsETHToETHrate = 1.10e18`.
4. Transaction mines. `viewSwapRsETHAmountAndFee(1.05 ether)` now computes:
   - `fee = 1.05e18 * feeBps / 10_000`
   - `amountAfterFee = 1.05e18 - fee`
   - `rsETHAmount = amountAfterFee * 1e18 / 1.10e18 ≈ 0.9545e18`
5. User receives `≈ 0.9545 rsETH` instead of the expected `≈ 1 rsETH` — a ~4.5 % shortfall — with no revert. [3](#0-2) [10](#0-9)

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

**File:** contracts/pools/RSETHPool.sol (L311-320)
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

**File:** contracts/pools/RSETHPool.sol (L326-347)
```text
    function viewSwapRsETHAmountAndFee(
        uint256 amount,
        address token
    )
        public
        view
        onlySupportedToken(token)
        returns (uint256 rsETHAmount, uint256 fee)
    {
        uint256 feeBpsForToken = tokenFeeBps[token];
        fee = amount * feeBpsForToken / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
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

**File:** contracts/LRTDepositPool.sol (L99-118)
```text
    function depositAsset(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedERC20Token(asset)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);

        emit AssetDeposit(msg.sender, asset, depositAmount, rsethAmountToMint, referralId);
    }
```
