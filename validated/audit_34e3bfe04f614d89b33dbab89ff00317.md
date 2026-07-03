### Title
Missing Minimum Output Slippage Guard on L2 Pool Deposit Functions - (File: contracts/pools/RSETHPoolV3.sol)

### Summary
All L2 pool `deposit()` functions across the RSETHPool suite accept ETH or supported tokens and mint wrsETH to the caller, but none of them accept a `minAmountOut` (minimum wrsETH) parameter. The rsETH/ETH exchange rate used to compute the mint amount is a cross-chain oracle value that can change between the time a user submits a transaction and when it is executed. Because no slippage floor is enforced, a depositor has no on-chain protection against receiving fewer wrsETH than they expected.

### Finding Description
`LRTDepositPool.depositETH` and `LRTDepositPool.depositAsset` on L1 both accept a `minRSETHAmountExpected` argument and revert with `MinimumAmountToReceiveNotMet` if the computed mint amount falls below it. [1](#0-0) [2](#0-1) 

The L2 pool equivalents provide no such parameter. `RSETHPoolV3.deposit(string referralId)` and `RSETHPoolV3.deposit(address token, uint256 amount, string referralId)` compute `rsETHAmount` directly from the current oracle rate and mint without any floor check: [3](#0-2) [4](#0-3) 

The same pattern is present in every other L2 pool variant: [5](#0-4) [6](#0-5) [7](#0-6) 

The rate consumed by all these pools is sourced from a `CrossChainRateReceiver` whose stored `rate` is updated asynchronously via LayerZero messages: [8](#0-7) 

The provider-side `updateRate()` function that pushes a new rate to L2 is permissionless — any caller can invoke it: [9](#0-8) 

Because rsETH is a yield-bearing token, its ETH price (`rsETHPrice`) only increases over time. A pending deposit transaction in the mempool is therefore vulnerable to a frontrunner who pays the LayerZero fee to push the latest (higher) rate to L2 before the deposit executes, causing the depositor to receive fewer wrsETH for the same ETH with no on-chain recourse.

### Impact Explanation
**Low — Contract fails to deliver promised returns, but doesn't lose value.**

A depositor who submits a transaction expecting `X` wrsETH may receive materially fewer wrsETH if the oracle rate is updated (legitimately or by a frontrunner) before their transaction is mined. The deposited ETH is not lost — it enters the pool — but the depositor's share of the pool is smaller than they agreed to. The L1 deposit path protects against exactly this scenario via `minRSETHAmountExpected`; the L2 paths do not.

### Likelihood Explanation
The rsETH/ETH rate increases continuously as EigenLayer rewards accrue and is pushed to L2 by anyone willing to pay the LayerZero messaging fee. Rate updates are routine operational events. Any deposit transaction that sits in the mempool for more than a few seconds during a rate-update window is exposed. No special privileges are required; the attack surface is every public `deposit()` call on every deployed L2 pool.

### Recommendation
Add a `uint256 minWrsETHAmountExpected` parameter to every L2 pool `deposit()` function and revert if the computed `rsETHAmount` is below it, mirroring the guard already present in `LRTDepositPool._beforeDeposit`:

```solidity
if (rsETHAmount < minWrsETHAmountExpected) revert MinimumAmountToReceiveNotMet();
```

### Proof of Concept
1. User submits `RSETHPoolV3.deposit{value: 10 ether}("ref")` to an L2 mempool. At submission time the oracle rate is `1.05e18` (1 rsETH = 1.05 ETH), so the user expects ≈ `9.52 wrsETH` (after fee).
2. Before the transaction is mined, an attacker calls `RSETHMultiChainRateProvider.updateRate()` on L1, paying the LayerZero fee. The new rate `1.10e18` is delivered to the L2 `CrossChainRateReceiver` and stored.
3. The user's deposit executes. `getRate()` now returns `1.10e18`. The user receives ≈ `9.09 wrsETH` — roughly 4.5% fewer than expected — with no revert, no warning, and no recourse.
4. The L1 equivalent `LRTDepositPool.depositETH(minRSETHAmountExpected, ...)` would have reverted at step 3, protecting the user. [10](#0-9) [11](#0-10) [12](#0-11)

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

**File:** contracts/pools/RSETHPoolV3.sol (L234-237)
```text
    /// @dev Gets the rate from the rsETHOracle
    function getRate() public view returns (uint256) {
        return IOracle(rsETHOracle).getRate();
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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L366-412)
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

    /// @dev Swaps supported token for rsETH
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

**File:** contracts/pools/RSETHPool.sol (L271-305)
```text
        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);

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

        IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId); // Add token address?
    }
```

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L289-301)
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

**File:** contracts/cross-chain/CrossChainRateProvider.sol (L85-101)
```text
    function updateRate() external payable nonReentrant {
        uint256 latestRate = getLatestRate();

        bytes memory remoteAndLocalAddresses = abi.encodePacked(rateReceiver, address(this));

        rate = latestRate;

        lastUpdated = block.timestamp;

        bytes memory _payload = abi.encode(latestRate);

        ILayerZeroEndpoint(layerZeroEndpoint).send{ value: msg.value }(
            dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
        );

        emit RateUpdated(rate);
    }
```

**File:** contracts/cross-chain/RSETHMultiChainRateProvider.sol (L26-28)
```text
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
    }
```
