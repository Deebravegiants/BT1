### Title
Missing Zero-Value Check on Computed rsETH Mint Amount Allows Depositor to Receive Zero Tokens - (File: contracts/LRTDepositPool.sol)

### Summary
`LRTDepositPool._beforeDeposit` computes `rsethAmountToMint` via integer division and then validates it only against the caller-supplied `minRSETHAmountExpected`. When `minRSETHAmountExpected = 0` (no enforcement on this parameter), the slippage guard `rsethAmountToMint < minRSETHAmountExpected` evaluates to `0 < 0 = false` and never reverts — even when `rsethAmountToMint` itself is 0. A depositor whose computed mint amount truncates to zero loses their deposited asset with no rsETH issued in return.

### Finding Description
`getRsETHAmountToMint` computes:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

Integer division truncates toward zero. When `amount * getAssetPrice(asset) < rsETHPrice()`, the result is 0. Because `rsETHPrice` grows monotonically with staking rewards (it starts at 1e18 and increases), any deposit where `amount * assetPrice < rsETHPrice` produces `rsethAmountToMint = 0`.

`_beforeDeposit` then checks:

```solidity
if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
```

There is no separate `require(rsethAmountToMint > 0)` guard. When `minRSETHAmountExpected = 0` — a value the protocol never rejects — the condition is `0 < 0 = false`, so execution continues. `_mintRsETH(0)` is called, minting nothing, while the depositor's ETH or LST has already been transferred in.

The same pattern appears across every L2 RSETHPool variant (`RSETHPool`, `RSETHPoolV2`, `RSETHPoolV3`, `RSETHPoolV2ExternalBridge`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`), all of which compute:

```solidity
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

and then unconditionally mint/transfer `rsETHAmount` with no zero-value guard and no slippage parameter at all.

### Impact Explanation
A depositor who passes `minRSETHAmountExpected = 0` (or uses any RSETHPool contract, which has no such parameter) and whose deposit amount is small enough that integer division truncates to zero will have their asset consumed by the protocol while receiving 0 rsETH/wrsETH. The protocol retains the deposited value; the user receives nothing. This matches the "Low" impact tier: the contract fails to deliver its promised return without the protocol itself losing value.

### Likelihood Explanation
`minAmountToDeposit` is not set in `initialize` and defaults to 0, so 1-wei deposits are accepted. With `rsETHPrice` already above 1e18 on mainnet (staking rewards have accrued), a 1-wei ETH or LST deposit produces `rsethAmountToMint = 0`. Any user who omits or zeroes the slippage parameter is silently harmed. On L2 RSETHPool contracts the risk is structural — there is no slippage parameter to set.

### Recommendation
Add an explicit non-zero check on the computed mint amount in `_beforeDeposit`:

```solidity
if (rsethAmountToMint == 0) revert ZeroRsETHMintAmount();
```

Apply the same guard in every RSETHPool `deposit` function after computing `rsETHAmount`. Additionally, consider enforcing `minRSETHAmountExpected > 0` at the call site, or at minimum documenting that passing 0 disables slippage protection entirely.

### Proof of Concept
1. `rsETHPrice` on mainnet is ~1.05e18 (5% staking appreciation).
2. Attacker (or naive user) calls `LRTDepositPool.depositETH{value: 1}(0, "")`.
3. `_beforeDeposit` runs: `depositAmount = 1`, passes `depositAmount == 0` check.
4. `getRsETHAmountToMint`: `(1 * 1e18) / 1.05e18 = 0` (integer truncation).
5. Slippage check: `0 < 0 = false` → no revert.
6. `_mintRsETH(0)` → 0 rsETH minted; user's 1 wei ETH is held by the pool.
7. On any RSETHPool L2 contract with `feeBps > 0` and a small `amount`, the same truncation occurs with no guard at all. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/LRTDepositPool.sol (L506-521)
```text
    function getRsETHAmountToMint(
        address asset,
        uint256 amount
    )
        public
        view
        override
        returns (uint256 rsethAmountToMint)
    {
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
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

**File:** contracts/pools/RSETHPoolV2.sol (L207-234)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused limitDailyMint(msg.value) {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }

    /// @dev view function to get the rsETH amount for a given amount of ETH
    /// @param amount The amount of ETH
    /// @return rsETHAmount The amount of rsETH that will be received
    /// @return fee The fee that will be charged
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
