### Title
Stale Stored `rsETHPrice` Used in `getRsETHAmountToMint()` Allows Depositors to Capture Unclaimed Yield from Existing Holders - (File: contracts/LRTDepositPool.sol)

---

### Summary
`LRTDepositPool.getRsETHAmountToMint()` divides by `lrtOracle.rsETHPrice()`, a **stored/cached** state variable, while simultaneously using `lrtOracle.getAssetPrice(asset)`, which fetches a **live** Chainlink price. The stored `rsETHPrice` is only updated when `updateRSETHPrice()` is explicitly called. Between updates, as yield accrues (stETH rebases, EigenLayer rewards), the true rsETH/ETH rate rises above the stored value. Any depositor who calls `depositETH()` or `depositAsset()` while the price is stale receives more rsETH than they are entitled to, diluting existing holders and capturing their unclaimed yield.

---

### Finding Description

`LRTOracle` stores the rsETH/ETH exchange rate in the state variable `rsETHPrice`:

```solidity
// contracts/LRTOracle.sol:28
uint256 public override rsETHPrice;
```

This value is only updated by an explicit call to `updateRSETHPrice()` (public, permissionless) or `updateRSETHPriceAsManager()` (manager-only), both of which invoke `_updateRsETHPrice()`. There is no automatic update triggered on deposit.

`LRTDepositPool.getRsETHAmountToMint()` uses this stored value as the denominator for minting:

```solidity
// contracts/LRTDepositPool.sol:520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

`lrtOracle.getAssetPrice(asset)` calls through to a live Chainlink feed (current price), but `lrtOracle.rsETHPrice()` returns the **last stored snapshot**. The two inputs to the division are therefore from different points in time.

`_beforeDeposit()` calls `getRsETHAmountToMint()` with no price refresh:

```solidity
// contracts/LRTDepositPool.sol:665
rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);
```

And both `depositETH()` and `depositAsset()` call `_beforeDeposit()` directly:

```solidity
// contracts/LRTDepositPool.sol:87, 111
uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);
uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);
```

The structural parallel to the external report is exact:
- **External report**: `SelfPeggingAsset` uses a locally stored `A` instead of fetching the current ramped value from `rampAController`, causing incorrect invariant calculations during the ramp window.
- **This repo**: `LRTDepositPool` uses a locally stored `rsETHPrice` instead of computing the current value from on-chain TVL, causing incorrect rsETH minting during the window between oracle updates.

---

### Impact Explanation

When yield accrues (e.g., stETH rebases, EigenLayer rewards flow in) but `updateRSETHPrice()` has not yet been called, the stored `rsETHPrice` is **lower** than the true current rate. A depositor of `X` ETH receives:

```
rsETH_minted = X / rsETHPrice_stored   >   X / rsETHPrice_true
```

The excess rsETH represents a claim on protocol TVL that was not contributed by the depositor — it is yield that belongs to existing holders. After `updateRSETHPrice()` is eventually called, the new price is computed over the enlarged supply, permanently diluting prior holders. This constitutes **theft of unclaimed yield** (High severity per the allowed impact scope).

---

### Likelihood Explanation

`updateRSETHPrice()` is called by an off-chain keeper on a periodic schedule (not on every block). The window between updates is a normal operating condition, not an edge case. Any depositor — no special role required — can call `depositETH()` or `depositAsset()` at any time. The attacker simply needs to deposit during the interval after yield has accrued but before the oracle is refreshed. This is a realistic, low-effort condition that recurs every update cycle.

---

### Recommendation

Atomically refresh `rsETHPrice` inside `_beforeDeposit()` (or inside `getRsETHAmountToMint()`) before computing the mint amount, so the denominator always reflects the current on-chain TVL. Alternatively, expose a view function in `LRTOracle` that computes the current rsETH price on-the-fly from `_getTotalEthInProtocol()` and `rsethSupply`, and use that in `getRsETHAmountToMint()` instead of the stored state variable.

---

### Proof of Concept

1. Protocol state: `rsethSupply = 1000 rsETH`, `rsETHPrice = 1.00 ETH` (stored), true TVL = 1050 ETH (50 ETH yield has accrued since last update; true price = 1.05 ETH).
2. `updateRSETHPrice()` has **not** been called yet.
3. Attacker calls `depositETH{value: 105 ETH}(minRSETH, "")`.
4. `getRsETHAmountToMint` computes: `105 ETH * 1e18 / 1.00e18 = 105 rsETH` (using stale price).
   - Correct amount at true price: `105 / 1.05 = 100 rsETH`.
   - Attacker receives **5 extra rsETH**.
5. Keeper calls `updateRSETHPrice()`. New supply = 1105 rsETH, TVL = 1155 ETH (1050 + 105 deposit). New price = `1155 / 1105 ≈ 1.0453 ETH`.
6. Attacker's 105 rsETH is worth `105 × 1.0453 ≈ 109.76 ETH` — a profit of ~4.76 ETH on a 105 ETH deposit, extracted from the yield that belonged to the original 1000 rsETH holders.

Relevant code locations: [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/LRTDepositPool.sol (L76-117)
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

    /// @notice helps user stake LST to the protocol
    /// @param asset LST asset address to stake
    /// @param depositAmount LST asset amount to stake
    /// @param minRSETHAmountExpected Minimum amount of rseth to receive
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

**File:** contracts/LRTOracle.sol (L214-250)
```text
    function _updateRsETHPrice() internal {
        address rsETHTokenAddress = lrtConfig.rsETH();
        uint256 rsethSupply = IRSETH(rsETHTokenAddress).totalSupply();

        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }

        if (highestRsethPrice == 0) {
            highestRsethPrice = rsETHPrice;
        }

        uint256 previousPrice = rsETHPrice;

        // get total ETH in the protocol (normalized to 1e18)
        uint256 totalETHInProtocol = _getTotalEthInProtocol();

        // calculate previousTVL using rsethSupply multiplied by rsETHPrice
        uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);

        IPausable lrtDepositPool = IPausable(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable withdrawalManager = IPausable(lrtConfig.getContract(LRTConstants.LRT_WITHDRAW_MANAGER));

        // determine if the protocol is active (not paused)
        bool protocolPaused = lrtDepositPool.paused() || withdrawalManager.paused() || paused;

        // only take fee if TVL increased and protocol is not paused
        uint256 protocolFeeInETH = 0;
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```
