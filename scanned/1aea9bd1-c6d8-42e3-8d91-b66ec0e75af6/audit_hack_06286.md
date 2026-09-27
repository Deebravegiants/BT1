# [M] Underflow can ruin mint from Alchemix logic

## Summary
Severity: Medium
Reporter: XKET
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L269
Type: audit-issue

## Details
# Underflow can ruin mint from Alchemix logic




## Summary
There can be an underflow in `Vault._calculate_max_mintable_amount` and it can ruin minting from Alchemix.

## Vulnerability Detail

`Vault._calculate_max_mintable_amount` gets `current_debt` from the first item of the result of `AlchemistV2.accounts`
```vyper
    current_debt: uint256 = convert(IAlchemist(self.alchemist).accounts(self)[0], uint256) 
```
And `AlchemistV2.accounts` returns `_calculateUnrealizedDebt` as the first item of the result.

```solidity
    function accounts(address owner)
        external view override
        returns (
            int256 debt,
            address[] memory depositedTokens
        )
    {
        Account storage account = _accounts[owner];

        return (
            _calculateUnrealizedDebt(owner),
            account.depositedTokens.values
        );
    }
```

In `_calculateUnrealizedDebt`, the return value is initialized by _accounts[owner].debt and then subtracted by unrealized credits.
```solidity
   function _calculateUnrealizedDebt(address owner) internal view returns (int256) {
        int256 debt = _accounts[owner].debt;

        Sets.AddressSet storage depositedTokens = _accounts[owner].depositedTokens;
        for (uint256 i = 0; i < depositedTokens.values.length; i++) {
            address yieldToken = depositedTokens.values[i];

            uint256 currentAccruedWeight = _yieldTokens[yieldToken].accruedWeight;
            uint256 lastAccruedWeight    = _accounts[owner].lastAccruedWeights[yieldToken];
            uint256 unlockedCredit       = _calculateUnlockedCredit(yieldToken);

            currentAccruedWeight += unlockedCredit > 0
                ? unlockedCredit * FIXED_POINT_SCALAR / _yieldTokens[yieldToken].totalShares
                : 0;

            if (currentAccruedWeight == lastAccruedWeight) {
                continue;
            }

            uint256 balance = _accounts[owner].balances[yieldToken];
            uint256 unrealizedCredit = ((currentAccruedWeight - lastAccruedWeight) * balance) / FIXED_POINT_SCALAR;

            debt -= SafeCast.toInt256(unrealizedCredit);
        }

        return debt;
    }
```

But the `_accounts[owner].debt` can be equal to or less than zero as noted in the comment of `AlchemistV2.sol`.

```solidity 
        // It is possible that the amount of debt which is repayable is equal to or less than zero after realizing the
        // credit that was earned since the last update. We do not want to perform a noop so we need to check that the
        // amount of debt to repay is greater than zero.
```

So `current_debt` can underflow in `Vault._calculate_max_mintable_amount`. If `_calculate_max_mintable_amount` returns huge result due to the underflow, this cap will not work.

```vyper
def _calculate_amount_to_mint(_amount_shares: uint256) -> uint256:
    return min(self._calculate_mintable_amount(_amount_shares), self._calculate_max_mintable_amount())
```

And mint more amount than expected from alchemix here.

```vyper
    amount_to_mint: uint256 = self._calculate_amount_to_mint(shares_issued)
    assert amount_to_mint > 0, "cannot mint new Alchemix debt"

    self._mint_from_alchemix(amount_to_mint, self.fund_receiver)
```

## Impact
Alchemix integration will be wrong.

## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L269
https://github.com/alchemix-finance/v2-contracts/blob/2b4ebfa619c4f3dd6ee48098a81e70ddb3369e53/contracts/AlchemistV2.sol#L143-L156
https://github.com/alchemix-finance/v2-contracts/blob/2b4ebfa619c4f3dd6ee48098a81e70ddb3369e53/contracts/AlchemistV2.sol#L1520-L1546
https://github.com/alchemix-finance/v2-contracts/blob/2b4ebfa619c4f3dd6ee48098a81e70ddb3369e53/contracts/AlchemistV2.sol#L718-L720
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L237-L238
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L227-L230

## Tool used
Manual Review

## Recommendation
Use safeCast equivalent instead of naive convert
