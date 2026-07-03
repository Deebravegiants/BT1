### Title
Stale `rsETHPrice` Read in Deposit and Withdrawal Paths Without Prior Update — (File: `contracts/LRTDepositPool.sol`, `contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTOracle.rsETHPrice` is a stored state variable updated only when `updateRSETHPrice()` is explicitly called. Neither `LRTDepositPool.depositETH`/`depositAsset` nor `LRTWithdrawalManager.initiateWithdrawal` call `updateRSETHPrice()` before reading `rsETHPrice` to compute mint or redemption amounts. When the stored price is stale and lower than the true current price (because yield has accrued but the keeper has not yet updated), depositors receive more rsETH than they deserve, stealing unclaimed yield from existing holders.

---

### Finding Description

`LRTOracle` stores the rsETH/ETH exchange rate in the state variable `rsETHPrice`. [1](#0-0) 

This value is only updated when `updateRSETHPrice()` (or its manager variant) is explicitly called: [2](#0-1) 

The update is performed by an off-chain keeper and is not called atomically inside any user-facing deposit or withdrawal function.

**Deposit path:** `LRTDepositPool.depositETH` and `depositAsset` both call `_beforeDeposit`, which calls `getRsETHAmountToMint`: [3](#0-2) 

The mint amount is computed as `(amount × assetPrice) / rsETHPrice`. Neither `depositETH` nor `depositAsset` calls `updateRSETHPrice()` before this read. [4](#0-3) [5](#0-4) 

**Withdrawal initiation path:** `LRTWithdrawalManager.initiateWithdrawal` calls `getExpectedAssetAmount`, which reads `rsETHPrice` directly: [6](#0-5) 

No call to `updateRSETHPrice()` precedes this read either. [7](#0-6) 

---

### Impact Explanation

**High — Theft of unclaimed yield.**

Between keeper updates, yield accrues in the protocol (staking rewards, EigenLayer rewards) but `rsETHPrice` remains at its last stored value, which is lower than the true current price. During this window:

- A depositor calling `depositETH`/`depositAsset` receives `(amount × assetPrice) / staleLowerPrice` rsETH — more than the correct amount at the true price.
- The excess rsETH represents yield that rightfully belongs to existing rsETH holders. The depositor captures it for free, diluting all current holders.

The inverse case (stale price higher than true price) is partially mitigated by the downside-protection pause in `_updateRsETHPrice`, but the upside-stale case (price not yet updated after yield accrual) is entirely unmitigated. [8](#0-7) 

---

### Likelihood Explanation

**Medium.** The keeper updates `rsETHPrice` periodically (not on every block). Any depositor who acts in the window between yield accrual and the next keeper update benefits from the stale price. No special privileges, front-running, or adversarial setup is required — the mis-accounting occurs for every deposit made while the price is stale. The longer the keeper interval, the larger the exploitable gap.

---

### Recommendation

- **Short term:** Inside `depositETH`, `depositAsset`, and `initiateWithdrawal`, call `ILRTOracle(lrtOracleAddress).updateRSETHPrice()` before reading `rsETHPrice`. Because `updateRSETHPrice` is `public` and `whenNotPaused`, this can be done atomically at the start of each function.
- **Long term:** Redesign `LRTOracle` so that `rsETHPrice` is always computed on-the-fly (as a `view` function) rather than stored, eliminating the possibility of a stale read. Alternatively, enforce that any function reading `rsETHPrice` must first trigger an update via a modifier.

---

### Proof of Concept

1. Protocol has 1000 ETH TVL, 1000 rsETH supply → `rsETHPrice = 1.0 ETH`. Keeper last ran 12 hours ago.
2. Over 12 hours, staking rewards add 10 ETH to TVL (now 1010 ETH). True price = 1.01 ETH. Keeper has not yet called `updateRSETHPrice()`, so `rsETHPrice` remains `1.0 ETH`.
3. Attacker calls `depositETH(100 ETH)`. `getRsETHAmountToMint` computes `100 × 1e18 / 1.0e18 = 100 rsETH`.
4. At the true price of 1.01 ETH, the attacker should receive `100 / 1.01 ≈ 99.01 rsETH`. Instead they receive `100 rsETH` — approximately 0.99 rsETH of excess, representing yield stolen from existing holders.
5. Keeper calls `updateRSETHPrice()`. New supply = 1100 rsETH, TVL = 1110 ETH → new price = `1110/1100 ≈ 1.009 ETH` instead of the correct `1010/1000 = 1.01 ETH` (before the deposit). Existing holders permanently lose a fraction of their accrued yield to the attacker. [9](#0-8) [10](#0-9)

### Citations

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L214-216)
```text
    function _updateRsETHPrice() internal {
        address rsETHTokenAddress = lrtConfig.rsETH();
        uint256 rsethSupply = IRSETH(rsETHTokenAddress).totalSupply();
```

**File:** contracts/LRTOracle.sol (L244-250)
```text
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
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

**File:** contracts/LRTWithdrawalManager.sol (L150-178)
```text
    function initiateWithdrawal(
        address asset,
        uint256 rsETHUnstaked,
        string calldata referralId
    )
        external
        override
        nonReentrant
        whenNotPaused
        onlySupportedAsset(asset)
        onlySupportedStrategy(asset)
    {
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }

        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);

        emit ReferralIdEmitted(referralId);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L580-594)
```text
    function getExpectedAssetAmount(
        address asset,
        uint256 amount
    )
        public
        view
        override
        returns (uint256 underlyingToReceive)
    {
        // setup oracle contract
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```
