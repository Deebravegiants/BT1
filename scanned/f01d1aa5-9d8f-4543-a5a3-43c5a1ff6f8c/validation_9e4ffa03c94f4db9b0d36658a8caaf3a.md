Now I have enough context to write the full finding. Let me read a few more lines to confirm the `agETH` pool pattern as well.

### Title
Fee-on-Transfer Token Mis-Accounting Inflates rsETH Minting, Causing Protocol Insolvency - (File: contracts/LRTDepositPool.sol)

---

### Summary

`LRTDepositPool.depositAsset` computes the rsETH amount to mint from the caller-supplied `depositAmount` **before** the token transfer occurs. If the deposited asset charges a transfer fee, the contract receives fewer tokens than `depositAmount`, yet mints rsETH as if the full amount arrived. Every such deposit over-mints rsETH relative to the actual backing, progressively making the protocol insolvent.

---

### Finding Description

In `LRTDepositPool.depositAsset`, the execution order is:

1. `rsethAmountToMint = _beforeDeposit(asset, depositAmount, ...)` — calls `getRsETHAmountToMint(asset, depositAmount)`, which computes `(depositAmount × assetPrice) / rsETHPrice`.
2. `IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount)` — for a fee-on-transfer token the contract actually receives `depositAmount − fee`.
3. `_mintRsETH(rsethAmountToMint)` — mints rsETH calculated from the **full** `depositAmount`, not the reduced amount actually held. [1](#0-0) 

`_beforeDeposit` is a pure view function; it never checks the contract's balance before or after the transfer: [2](#0-1) 

`getRsETHAmountToMint` uses the raw `amount` argument with no balance-delta guard: [3](#0-2) 

The same structural flaw is present in every L2 pool `deposit(token, amount, referralId)` overload — `safeTransferFrom` is called with `amount`, then `viewSwapRsETHAmountAndFee(amount, token)` is called with the same unverified `amount`, and wrsETH is minted for the full value: [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7) [9](#0-8) 

`RsETHTokenWrapper._deposit` has the same pattern — it mints `_amount` of wrsETH but only receives `_amount − fee` of the underlying token: [10](#0-9) 

---

### Impact Explanation

**Critical — Protocol insolvency.**

Each deposit with a fee-on-transfer token mints more rsETH (or wrsETH) than the actual asset value received. The rsETH price is computed from total assets divided by total supply (`rsETHPrice = totalAssets / rsETHSupply`). Over-minting rsETH without a matching asset increase dilutes the exchange rate for all existing holders. Repeated deposits drain the protocol's backing, eventually making it impossible for all rsETH holders to redeem at par — a classic insolvency scenario. In the L2 pool case the pool's wrsETH reserve is depleted faster than the token collateral it holds, causing the pool to run out of wrsETH to pay legitimate depositors.

---

### Likelihood Explanation

**Medium.** The currently deployed supported assets (stETH, rETH, cbETH, swETH, etc.) are not fee-on-transfer tokens. However, the protocol's governance can add new supported assets via `LRTConfig`, and the contracts contain no guard preventing a fee-on-transfer token from being whitelisted. If any such token is ever added — or if an existing token introduces a fee via an upgrade — the vulnerability becomes immediately exploitable by any unprivileged depositor calling `depositAsset` or the pool `deposit` functions.

---

### Recommendation

Use a balance-delta pattern to determine the actual amount received, and use that value for minting:

```solidity
function depositAsset(
    address asset,
    uint256 depositAmount,
    uint256 minRSETHAmountExpected,
    string calldata referralId
) external nonReentrant whenNotPaused onlySupportedERC20Token(asset) {
    // capture balance before transfer
    uint256 balanceBefore = IERC20(asset).balanceOf(address(this));
    IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
    uint256 actualReceived = IERC20(asset).balanceOf(address(this)) - balanceBefore;

    // use actualReceived, not depositAmount, for all downstream calculations
    uint256 rsethAmountToMint = _beforeDeposit(asset, actualReceived, minRSETHAmountExpected);
    _mintRsETH(rsethAmountToMint);

    emit AssetDeposit(msg.sender, asset, actualReceived, rsethAmountToMint, referralId);
}
```

Apply the same balance-delta pattern to every pool `deposit(token, amount, referralId)` overload and to `RsETHTokenWrapper._deposit`.

---

### Proof of Concept

1. Governance adds a fee-on-transfer LST (e.g., a token that deducts 1% on every transfer) as a supported asset in `LRTConfig`.
2. Attacker calls `LRTDepositPool.depositAsset(feeToken, 1000e18, 0, "")`.
3. `_beforeDeposit` computes `rsethAmountToMint` based on `1000e18`.
4. `safeTransferFrom` transfers `1000e18` from attacker; contract receives `990e18` (1% fee deducted).
5. `_mintRsETH` mints rsETH equivalent to `1000e18` of the asset.
6. The attacker holds rsETH backed by `1000e18` worth of asset, but the pool only holds `990e18` — a 10e18 shortfall per deposit.
7. Repeating this drains the protocol's backing assets, reducing the rsETH exchange rate for all holders. [11](#0-10) [3](#0-2)

### Citations

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

**File:** contracts/pools/RSETHPoolV3.sol (L282-293)
```text
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
    }
```

**File:** contracts/pools/RSETHPool.sol (L294-305)
```text
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId); // Add token address?
    }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L260-271)
```text
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        rsETH.safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId); // Add token address?
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L401-412)
```text
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
    }
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L318-329)
```text
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
    }
```

**File:** contracts/agETH/AGETHPoolV3.sol (L143-154)
```text
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 agETHAmount, uint256 fee) = viewSwapAgETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        agETH.mint(msg.sender, agETHAmount);

        emit SwapOccurred(msg.sender, agETHAmount, fee, referralId);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L134-141)
```text
    function _deposit(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);

        _mint(_to, _amount);
        emit Deposit(_asset, msg.sender, _to, _amount);
    }
```
