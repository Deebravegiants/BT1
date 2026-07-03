### Title
No Slippage Protection on `deposit()` in L2 RSETHPool Contracts - (`contracts/pools/RSETHPoolV3.sol`, `contracts/pools/RSETHPoolV3ExternalBridge.sol`, `contracts/pools/RSETHPoolV3WithNativeChainBridge.sol`, `contracts/pools/RSETHPoolNoWrapper.sol`, `contracts/pools/RSETHPoolV2.sol`)

---

### Summary

All L2 liquidity pool `deposit()` functions compute the `wrsETH` (or `rsETH`) amount to mint using a live oracle rate but accept no `minRSETHAmountOut` parameter. A user who submits a deposit transaction while the oracle rate is at value `R` may have their transaction executed after the rate has been updated to `R'` (where `R' > R`), receiving fewer tokens than expected with no on-chain recourse.

---

### Finding Description

Every L2 pool variant exposes one or two `deposit()` overloads (ETH and token). In each case, the minted amount is computed as:

```solidity
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

where `rsETHToETHrate = getRate()` reads from an oracle at execution time.

**`RSETHPoolV3.sol` — ETH deposit:** [1](#0-0) 

**`RSETHPoolV3.sol` — token deposit:** [2](#0-1) 

**`RSETHPoolV3ExternalBridge.sol` — ETH deposit:** [3](#0-2) 

**`RSETHPoolV3WithNativeChainBridge.sol` — ETH deposit:** [4](#0-3) 

**`RSETHPoolNoWrapper.sol` — ETH deposit:** [5](#0-4) 

**`RSETHPoolV2.sol` — ETH deposit:** [6](#0-5) 

None of these functions accept or enforce a minimum output amount.

The oracle rate is sourced from `CrossChainRateReceiver.getRate()`, which is updated asynchronously via LayerZero messages from L1: [7](#0-6) 

Alternatively, on some deployments, `InterimRSETHOracle` is used, where a MANAGER role can update the rate at any time: [8](#0-7) 

**Contrast with L1:** The L1 `LRTDepositPool.depositETH()` and `depositAsset()` both accept a `minRSETHAmountExpected` parameter and enforce it in `_beforeDeposit()`: [9](#0-8) [10](#0-9) 

The L2 pool contracts have no equivalent protection.

---

### Impact Explanation

When the rsETH/ETH oracle rate increases between a user's transaction submission and its on-chain execution, the user receives fewer `wrsETH` tokens than they observed in the view function at submission time. Since `wrsETH` is pegged 1:1 to `rsETH` and each `rsETH` is worth more ETH at the higher rate, the user's deposited ETH value is preserved — they are not drained of funds. However, the contract fails to deliver the token quantity the user expected at submission time.

**Impact: Low — Contract fails to deliver promised returns, but doesn't lose value.**

---

### Likelihood Explanation

The rsETH/ETH rate increases monotonically over time as EigenLayer staking rewards accrue. Rate updates are pushed periodically from L1 to L2 via LayerZero. Any user whose deposit transaction is pending in the mempool at the moment a rate update lands will receive fewer tokens than the UI quoted. This is a routine, recurring scenario requiring no attacker action — it is a structural property of the protocol's asynchronous rate propagation model.

---

### Recommendation

Add a `minRSETHAmountOut` parameter to all `deposit()` overloads in every L2 pool contract and revert if the computed amount falls below it:

```diff
- function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
+ function deposit(string memory referralId, uint256 minRSETHAmountOut) external payable nonReentrant whenNotPaused {
      ...
      (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
+     if (rsETHAmount < minRSETHAmountOut) revert InsufficientOutputAmount();
      ...
  }
```

Apply the same pattern to the token `deposit(address token, uint256 amount, string memory referralId)` overloads across `RSETHPoolV3.sol`, `RSETHPoolV3ExternalBridge.sol`, `RSETHPoolV3WithNativeChainBridge.sol`, `RSETHPoolNoWrapper.sol`, and `RSETHPoolV2.sol`. The UI should pre-compute the expected output via `viewSwapRsETHAmountAndFee` and pass a user-configurable slippage tolerance (e.g. 0.1%) as `minRSETHAmountOut`.

---

### Proof of Concept

1. User calls `viewSwapRsETHAmountAndFee(1 ether)` on `RSETHPoolV3`. Oracle rate is `1.05e18` (rsETH costs 1.05 ETH). Expected output: `~0.952 wrsETH`.
2. User submits `deposit{value: 1 ether}("ref")`.
3. Before the tx is mined, a LayerZero message updates the oracle rate to `1.06e18`.
4. Transaction executes: `rsETHAmount = 1e18 * 1e18 / 1.06e18 ≈ 0.943 wrsETH`.
5. User receives `~0.943 wrsETH` instead of the expected `~0.952 wrsETH` — approximately 0.9% fewer tokens — with no on-chain protection and no revert. [11](#0-10) [12](#0-11)

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

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L82-100)
```text
    function lzReceive(uint16 _srcChainId, bytes memory _srcAddress, uint64, bytes calldata _payload) external {
        require(msg.sender == layerZeroEndpoint, "Sender should be lz endpoint");

        address srcAddress;
        assembly {
            srcAddress := mload(add(_srcAddress, 20))
        }

        require(_srcChainId == srcChainId, "Src chainId must be correct");
        require(srcAddress == rateProvider, "Src address must be provider");

        uint256 _rate = abi.decode(_payload, (uint256));

        rate = _rate;

        lastUpdated = block.timestamp;

        emit RateUpdated(_rate);
    }
```

**File:** contracts/pools/oracle/InterimRSETHOracle.sol (L36-44)
```text
    function setRate(uint256 newRate) external onlyRole(MANAGER_ROLE) {
        _setRate(newRate);
    }

    /// @dev Internal function to set the rsETH/ETH rate
    function _setRate(uint256 newRate) internal {
        if (newRate < 1e18) revert InvalidRate();
        rate = newRate;
        emit RateUpdated(newRate);
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

**File:** contracts/LRTDepositPool.sol (L665-669)
```text
        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
```
