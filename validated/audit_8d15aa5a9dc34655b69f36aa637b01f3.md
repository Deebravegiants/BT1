### Title
Zero rsETH Minted on Dust Deposits Due to Truncating Division in `getRsETHAmountToMint` - (File: contracts/LRTDepositPool.sol)

---

### Summary

`LRTDepositPool.getRsETHAmountToMint()` computes the rsETH to mint using plain integer division, which truncates toward zero. When a depositor supplies a sufficiently small asset amount (or passes `minRSETHAmountExpected = 0`), the computed mint amount rounds to zero. Because `depositAsset()` transfers the user's assets before minting, the user's tokens are consumed by the contract while zero rsETH is issued in return.

---

### Finding Description

`getRsETHAmountToMint` in `LRTDepositPool.sol` computes:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [1](#0-0) 

This is Solidity integer division — it truncates (rounds down). The result is zero whenever:

```
amount * assetPrice < rsETHPrice
```

For ETH-pegged LSTs (`assetPrice ≈ 1e18`) and a `rsETHPrice` that has grown above `1e18` (which occurs as soon as any staking rewards accrue), a deposit of 1 wei satisfies this condition and yields `rsethAmountToMint = 0`.

The guard in `_beforeDeposit` only checks:

```solidity
if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
``` [2](#0-1) 

When the caller passes `minRSETHAmountExpected = 0` (a valid argument), the condition `0 < 0` is false and no revert occurs. Execution continues into `depositAsset`:

```solidity
IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
_mintRsETH(rsethAmountToMint);   // rsethAmountToMint == 0
``` [3](#0-2) 

The user's assets are pulled into the pool, and `RSETH.mint(msg.sender, 0)` is called. OpenZeppelin's `_mint` does not revert on a zero amount, so the transaction succeeds silently. The user receives nothing. [4](#0-3) 

The `minAmountToDeposit` guard only blocks `depositAmount == 0` when `minAmountToDeposit` is at its default value of zero:

```solidity
if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
    revert InvalidAmountToDeposit();
}
``` [5](#0-4) 

A 1-wei deposit passes this check.

---

### Impact Explanation

A depositor who calls `depositAsset(asset, 1, 0, "")` (or any amount small enough that `amount * assetPrice < rsETHPrice`) loses their deposited tokens: the assets are transferred to `LRTDepositPool` and increase the protocol TVL (benefiting all existing rsETH holders), while the caller receives zero rsETH. The contract fails to deliver the promised return for the deposited amount.

**Impact class**: Low — Contract fails to deliver promised returns, but doesn't lose value at the protocol level.

---

### Likelihood Explanation

- `rsETHPrice` exceeds `1e18` as soon as any staking rewards are reflected, which is the normal operating state of the protocol.
- `minAmountToDeposit` defaults to `0` and is only set by admin action; many deployments may leave it unset.
- Any caller who omits a slippage guard (`minRSETHAmountExpected = 0`) and deposits a dust amount (1 wei) triggers the bug.
- Integrating contracts (e.g., routers, aggregators) that do not enforce a minimum received amount are particularly at risk.

**Likelihood**: Low — requires a dust-sized deposit with no slippage protection, but the conditions are realistic for naive integrators or users.

---

### Recommendation

1. **Add an explicit zero-mint guard** in `_beforeDeposit`:
   ```solidity
   if (rsethAmountToMint == 0) revert ZeroRsETHMinted();
   ```
2. **Set a non-zero `minAmountToDeposit`** at initialization to ensure deposits always produce at least 1 wei of rsETH.
3. **Document** that callers must pass a non-zero `minRSETHAmountExpected` to protect against rounding losses, analogous to slippage protection in AMMs.

---

### Proof of Concept

Assume:
- `rsETHPrice = 1.05e18` (5% staking appreciation — realistic after months of operation)
- `assetPrice = 1e18` (ETH-pegged LST)
- `minAmountToDeposit = 0` (default)

Attacker/user calls:
```solidity
depositPool.depositAsset(stETH, 1, 0, "");
```

Step-by-step:
1. `_beforeDeposit(stETH, 1, 0)` is entered.
2. `getRsETHAmountToMint(stETH, 1)` computes `(1 * 1e18) / 1.05e18 = 0` (integer truncation).
3. Check: `0 < 0` → false → no revert.
4. `IERC20(stETH).safeTransferFrom(msg.sender, depositPool, 1)` — 1 wei of stETH leaves the user.
5. `RSETH.mint(msg.sender, 0)` — zero rsETH is minted.
6. Transaction succeeds; user's 1 wei is permanently absorbed into the pool TVL. [6](#0-5) [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/LRTDepositPool.sol (L113-116)
```text
        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);

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

**File:** contracts/LRTDepositPool.sol (L684-690)
```text
    /// @dev private function to mint rseth
    /// @param rsethAmountToMint Amount of rseth minted
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
