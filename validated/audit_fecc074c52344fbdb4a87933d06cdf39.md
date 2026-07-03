### Title
Fee-on-Transfer Token Support Causes rsETH Over-Minting and Existing Holder Dilution - (File: contracts/LRTDepositPool.sol)

### Summary

`LRTDepositPool.depositAsset()` calculates the rsETH amount to mint using the caller-supplied `depositAmount` parameter, then performs `safeTransferFrom` with that same value. If the underlying LST asset charges a fee on transfer, the contract receives fewer tokens than `depositAmount`, but mints rsETH as if the full `depositAmount` arrived. This inflates the rsETH supply relative to actual protocol TVL, diluting all existing rsETH holders.

### Finding Description

In `depositAsset`, the flow is:

1. `rsethAmountToMint = _beforeDeposit(asset, depositAmount, ...)` — computes rsETH to mint using the raw `depositAmount`.
2. `IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount)` — transfers tokens; if the token charges a transfer fee, only `depositAmount - fee` arrives.
3. `_mintRsETH(rsethAmountToMint)` — mints rsETH calculated from the full `depositAmount`, not the actual received amount.

`getRsETHAmountToMint` computes:

```
rsethAmountToMint = (depositAmount * assetPrice) / rsETHPrice
```

The actual tokens received are `depositAmount - transferFee`, but rsETH minted corresponds to `depositAmount`. The rsETH price (`rsETHPrice`) is derived from `_getTotalEthInProtocol()`, which calls `getTotalAssetDeposits()`, which reads `IERC20(asset).balanceOf(address(this))` — the real on-chain balance. So the oracle-tracked TVL reflects the lower actual balance, while the rsETH supply is inflated. Every such deposit permanently lowers the rsETH price for all holders.

The same pattern exists in `RSETHPoolV3.deposit(token, amount, referralId)`, `RSETHPoolNoWrapper.deposit(token, amount, referralId)`, and `RSETHPoolV3ExternalBridge.deposit(token, amount, referralId)`, where `viewSwapRsETHAmountAndFee(amount, token)` is called with the nominal `amount` but only `amount - fee` is received.

### Impact Explanation

Every deposit of a fee-on-transfer LST mints more rsETH than the deposited value warrants. The rsETH price, recalculated from actual on-chain balances, will be lower than it should be. All existing rsETH holders suffer a permanent reduction in the ETH value their rsETH represents. This constitutes theft of yield from existing holders proportional to the transfer fee and deposit volume.

**Impact: High — Theft of unclaimed yield / permanent dilution of existing rsETH holders.**

### Likelihood Explanation

The protocol's `addNewSupportedAsset` (via `TIME_LOCK_ROLE`) allows new LST tokens to be added. Some LST tokens or stablecoins (e.g., USDT, which has a dormant fee switch) could activate transfer fees after being listed. The vulnerability is also present in the pool contracts for any token added via `addSupportedToken`. No attacker action is required beyond a normal deposit call once a fee-on-transfer token is supported.

**Likelihood: Medium** — requires a fee-on-transfer token to be listed, which is a realistic governance/upgrade scenario.

### Recommendation

Use a balance-before/balance-after pattern to determine the actual received amount, and base rsETH minting on that:

```solidity
uint256 balanceBefore = IERC20(asset).balanceOf(address(this));
IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
uint256 actualReceived = IERC20(asset).balanceOf(address(this)) - balanceBefore;

uint256 rsethAmountToMint = getRsETHAmountToMint(asset, actualReceived);
// then mint based on actualReceived
```

Alternatively, explicitly document and enforce that only non-fee-on-transfer tokens may be added as supported assets, and add a check in `addNewSupportedAsset`.

### Proof of Concept

1. Protocol lists a token `FOT` (fee-on-transfer, 1% fee) as a supported asset.
2. Alice calls `depositAsset(FOT, 1000e18, 0, "")`.
3. `_beforeDeposit` computes `rsethAmountToMint` based on `1000e18`.
4. `safeTransferFrom` transfers `1000e18` from Alice; contract receives `990e18` (1% fee taken).
5. `_mintRsETH` mints rsETH for `1000e18` worth of FOT.
6. `rsETHPrice` is next updated via `_getTotalEthInProtocol()` → `getTotalAssetDeposits(FOT)` → `IERC20(FOT).balanceOf(depositPool)` = `990e18`.
7. rsETH supply is inflated by the equivalent of `10e18` FOT worth of rsETH, permanently diluting all prior holders.

**Root cause references:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/LRTDepositPool.sol (L110-117)
```text
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);

        emit AssetDeposit(msg.sender, asset, depositAmount, rsethAmountToMint, referralId);
```

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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L390-412)
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
