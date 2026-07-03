### Title
Depositor Permanently Loses Funds When Integer Division Rounds `rsethAmountToMint` to Zero - (File: contracts/LRTDepositPool.sol)

### Summary
`LRTDepositPool.depositETH()` and `depositAsset()` silently accept a deposit and take the user's funds while minting **zero rsETH** whenever the deposit amount is too small for the integer division in `getRsETHAmountToMint()` to produce a non-zero result. The user's assets are permanently locked in the pool with no recovery path.

### Finding Description

`_beforeDeposit()` computes the rsETH amount to mint via:

```solidity
// LRTDepositPool.sol line 665
rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);
```

`getRsETHAmountToMint()` performs integer division:

```solidity
// LRTDepositPool.sol line 520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

When `amount * assetPrice < rsETHPrice`, Solidity integer division truncates the result to **0**.

The only guard after this calculation is:

```solidity
// LRTDepositPool.sol line 667-669
if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
```

If the caller passes `minRSETHAmountExpected = 0` (the natural default for a naive integrator or direct caller), the condition `0 < 0` is false and execution continues. `_mintRsETH(0)` is then called, which calls `RSETH.mint(msg.sender, 0)`. OpenZeppelin's `_mint` with `amount = 0` is a no-op — it succeeds silently. The user's ETH (for `depositETH`) or LST (for `depositAsset`) is already in the contract and is never returned.

The entry-point check:

```solidity
// LRTDepositPool.sol line 657-659
if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
    revert InvalidAmountToDeposit();
}
```

only blocks `depositAmount == 0` when `minAmountToDeposit` is at its default value of `0` (no explicit initialization in `initialize()`). Any non-zero `depositAmount` that is still too small to mint 1 rsETH passes this check.

**Concrete example:** Once rsETH appreciates to 1.5 ETH per rsETH (`rsETHPrice = 1.5e18`), a user depositing 1 wei of ETH computes `(1 * 1e18) / 1.5e18 = 0`. The 1 wei is taken; 0 rsETH is minted. For LST assets priced below rsETH, the threshold is even larger.

### Impact Explanation

The depositor's funds are permanently transferred into `LRTDepositPool` with no rsETH minted in return. There is no withdrawal mechanism for a user holding 0 rsETH. The ETH/LST is effectively donated to the pool, marginally inflating the rsETH price for all existing holders. This constitutes a direct, permanent loss of user funds — matching **Critical: Direct theft of any user funds**.

### Likelihood Explanation

Any unprivileged user calling `depositETH` or `depositAsset` with a small amount and `minRSETHAmountExpected = 0` triggers this. As rsETH appreciates over time, the minimum deposit required to mint 1 rsETH grows, widening the vulnerable range. Automated integrators, bots, or users who omit the slippage parameter are realistic victims.

### Recommendation

Add an explicit zero-shares guard in `_beforeDeposit()` immediately after computing `rsethAmountToMint`:

```solidity
rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);
if (rsethAmountToMint == 0) revert ZeroRsETHMinted();
```

Alternatively, enforce a non-zero `minAmountToDeposit` that is kept calibrated to always produce at least 1 rsETH at the current price.

### Proof of Concept

1. rsETH price appreciates to `1.5e18` (1.5 ETH per rsETH) via `LRTOracle.rsETHPrice`.
2. Attacker (or naive user) calls `LRTDepositPool.depositETH{value: 1}(0, "")`.
3. `_beforeDeposit(ETH_TOKEN, 1, 0)` is entered.
4. `depositAmount == 0` → false; `depositAmount < minAmountToDeposit` → `1 < 0` → false. Check passes.
5. `getRsETHAmountToMint(ETH_TOKEN, 1)` → `(1 * 1e18) / 1.5e18` → `0`.
6. `0 < 0` → false. `MinimumAmountToReceiveNotMet` is not thrown.
7. `_mintRsETH(0)` → `RSETH.mint(msg.sender, 0)` → `_mint(msg.sender, 0)` → no-op.
8. User's 1 wei ETH is permanently locked in `LRTDepositPool`; user holds 0 rsETH. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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

**File:** contracts/LRTDepositPool.sol (L686-690)
```text
    function _mintRsETH(uint256 rsethAmountToMint) private {
        address rsethToken = lrtConfig.rsETH();
        // mint rseth for user
        IRSETH(rsethToken).mint(msg.sender, rsethAmountToMint);
    }
```

**File:** contracts/RSETH.sol (L229-240)
```text
    function mint(
        address to,
        uint256 amount
    )
        external
        onlyRole(LRTConstants.MINTER_ROLE)
        whenNotPaused
        checkDailyMintLimit(amount)
    {
        _enforceNotBlocked(to);
        _mint(to, amount);
    }
```
