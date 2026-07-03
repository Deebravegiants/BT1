Audit Report

## Title
Dust Deposit Yields Zero rsETH Due to Uninitialized `minAmountToDeposit` and Missing Zero-Mint Guard - (File: contracts/LRTDepositPool.sol)

## Summary
`LRTDepositPool` never initializes `minAmountToDeposit` in `initialize()`, leaving it at zero. Combined with integer-division truncation in `getRsETHAmountToMint()` and the absence of a zero-rsETH guard in `_beforeDeposit()`, any caller who deposits a sufficiently small LST amount with `minRSETHAmountExpected = 0` will have their tokens permanently transferred to the protocol while receiving zero rsETH. The absorbed dust inflates TVL and silently redistributes value to all existing rsETH holders.

## Finding Description
**Root cause 1 — uninitialized `minAmountToDeposit`.**
`minAmountToDeposit` is declared at line 30 but never assigned in `initialize()` (lines 45–52), so it starts at `0`. `setMinAmountToDeposit()` (lines 282–285) accepts any value including zero, imposing no lower bound.

**Root cause 2 — dust passes the deposit guard.**
`_beforeDeposit` (lines 657–659) only rejects `depositAmount == 0` or `depositAmount < minAmountToDeposit`. When `minAmountToDeposit == 0`, every non-zero deposit passes unconditionally.

**Root cause 3 — integer division truncates to zero.**
`getRsETHAmountToMint` (lines 519–520) computes:
```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```
For a 1-wei deposit with `getAssetPrice ≈ 1e18` and `rsETHPrice = 1.05e18`: `(1 × 1e18) / 1.05e18 = 0`.

**Root cause 4 — no zero-rsETH guard.**
`_beforeDeposit` (lines 665–669) checks `rsethAmountToMint < minRSETHAmountExpected`. When the caller passes `minRSETHAmountExpected = 0`, a zero result satisfies `0 < 0 == false` and passes silently.

**Exploit path.**
`depositAsset` (lines 113–115) then executes `safeTransferFrom(user → pool, dustAmount)` followed by `_mintRsETH(0)` (lines 686–690), minting nothing for the user while permanently absorbing their tokens.

## Impact Explanation
A depositor who supplies a dust LST amount with `minRSETHAmountExpected = 0` loses their tokens to the protocol and receives zero rsETH. The absorbed dust raises the protocol's total asset value, which increases `rsETHPrice` on the next oracle update, silently redistributing value to all existing rsETH holders at the depositor's expense. This matches **Low: Contract fails to deliver promised returns, but doesn't lose value** — the protocol gains value; the depositor does not.

## Likelihood Explanation
The condition is present in the default deployment state: `minAmountToDeposit` is never set in `initialize()`, so no admin action is required to enable the vulnerable path. Any unprivileged external caller who passes `minRSETHAmountExpected = 0` (a common default in scripts and integrations) and deposits a sufficiently small amount triggers the issue. Likelihood is **Low** because the per-transaction loss is dust-sized, but the precondition is always satisfied post-deployment without any configuration.

## Recommendation
1. **Initialize `minAmountToDeposit` to a safe non-zero value** inside `initialize()` (e.g., `0.001 ether`).
2. **Add a lower bound in `setMinAmountToDeposit()`** — reject values below a protocol-defined minimum, mirroring the pattern in `KernelVaultETH.setMinDeposit()` (lines 305–308) which reverts on zero.
3. **Add an explicit zero-rsETH guard in `_beforeDeposit()`** after computing `rsethAmountToMint`:
   ```solidity
   if (rsethAmountToMint == 0) revert InvalidAmountToDeposit();
   ```

## Proof of Concept
```
State:  minAmountToDeposit = 0 (default, never initialized)
        rsETHPrice = 1.05e18 (5% appreciation post-launch)
        stETH assetPrice = 1e18

1. User calls: depositAsset(stETH, 1 wei, minRSETHAmountExpected=0, "")

2. _beforeDeposit (L657):
   1 == 0? No.
   1 < 0?  No. → passes

3. getRsETHAmountToMint(stETH, 1) (L520):
   = (1 * 1e18) / 1.05e18 = 0  (integer truncation)

4. _beforeDeposit (L667):
   0 < 0? No. → passes

5. safeTransferFrom(user, depositPool, 1 wei stETH) → user loses 1 wei stETH (L114)
6. _mintRsETH(0) → IRSETH.mint(user, 0) → user receives 0 rsETH (L689)

Result: 1 wei stETH permanently absorbed; rsETH supply unchanged;
        next rsETHPrice update benefits all existing holders.
```

Foundry test plan: deploy `LRTDepositPool` with a mock oracle returning `rsETHPrice = 1.05e18` and `getAssetPrice = 1e18`; call `depositAsset(mockLST, 1, 0, "")` from an unprivileged address; assert `IRSETH.balanceOf(caller) == 0` and `IERC20(mockLST).balanceOf(depositPool) == 1`.