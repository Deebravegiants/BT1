# [H] FYTokens can be minted for free

## Summary
Severity: High
Chain: Smart contract
Component: 2021-05-yield
Published: 2021-06-01
Source: https://github.com/code-423n4/2021-05-yield-findings/issues/28
Type: code-finding

## Details
# Handle

cmichel


# Vulnerability details

The core issue is that one can force the protocol to do an arbitrary trade in the pool using `Ladle._roll`. The function allows specifying a base amount and the protocol will mint as many fyTokens as needed for the trade, and trade them in the pool.

This can be used for a sandwich attack by forcing the protocol to mint fyTokens and trade them for underlying in an imbalanced pool with bad prices.

```solidity
// Calculate debt in old fyToken terms
uint128 amt = _debtInBase(vault.seriesId, series, balances.art);

// Mint new fyToken to the pool, as a kind of flash loan
// @audit: loan can be set to 255
newFyToken.mint(address(pool), amt * loan);

// Buy the base required to pay off the debt in series 1, and find out the debt in series 2
// @audit: this buys the old debt (amt) at a bad price
newDebt = pool.buyBase(address(baseJoin), amt, max);
baseJoin.join(address(baseJoin), amt); // Repay the old series debt

pool.retrieveFYToken(address(newFyToken)); // Get the surplus fyToken
newFyToken.burn(address(newFyToken), (amt * loan) - newDebt); // Burn the surplus
```


The attack works like this:
1. Create a vault for an `oldSeries` with some collateral (ink) and debt (art) (collateral can also be flashloaned)
2. Flashloan lots of fyTokens of `newSeries` (for example totalSupply / 2)
3. Dump them into the base <> fyToken pool (of `newSeries`) to receive base tokens. The pool is now imbalanced and has a large fyToken reserve and a low base reserve
4. Call `Ladle._roll(vaultId, vault, newSeriesId, loan=255, max=typeof(uint128).max)` (using `batch`). This will calculate the amount of fyTokens needed to repay the vault's old debt (`balances.art`) which is a high value because of the unbalanced pool in 3). It then mints and swaps a large amount of fyTokens for the old debt amount. The pool's fyToken reserve has increased by a large amount again and the base tokens only by a (comparably) small amount.
5. Perform the final sandwich attack trade by trading back the gained `base` amount from 3) in the pool. The trade will return a much larger fyToken amount than one had to pay in 3) due to the bad trade of the protocol at step 4). One makes a profit in fyTokens
6. Repay the fyTokens flashloan. Use the profit to dump it further in the pool for more base tokens or redeem it later for base from the **Join** using `fyToken.redeem`.
(7. Repay the vault setup flashloan)


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2021-05-yield-findings/issues/28_
