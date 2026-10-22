# [H] denial of service

## Summary
Severity: High
Chain: Smart contract
Component: 2021-12-vader
Published: 2021-12-22
Source: https://github.com/code-423n4/2021-12-vader-findings/issues/98
Type: code-finding

## Details
# Handle

danb


# Vulnerability details

https://github.com/code-423n4/2021-12-vader/blob/main/contracts/dex-v2/pool/VaderPoolV2.sol#L334
on the first deposit, the total liquidity is set to `nativeDeposit`.
this might be a very low number compared to `foreignDeposit`.
It can cause a denial of service of the pair.
## Impact
A pair can enter a denial of service state.
## Proof of Concept
consider the following scenario:
the owner of the pool calls `setFungibleTokenSupport` for a new token, for example weth.
a malicious actor calls `mintFungible`,  with `nativeDeposit == 1` and `foreignDeposit == 10 ether`.
`totalLiquidityUnits` will be 1.
the pool can be arbitraged, even by the attacker, but `totalLiquidityUnits` will still be 1.
this means that 1 liquidity token is equal to all of the pool reserves, which is a lot of money.
It will cause a very high rounding error for anyone trying to mint liquidity.
then, anyone who will try to mint liquidity will either:
1) fail, because they can't mint 0 liquidity if their amount is too small.
2) get less liquidity tokens than they should, because there is a very high rounding error, and its against new liquidity providers.
The rounding error losses will increase the pool reserves, which will increase value of liquidity tokens, so the hacker can even profit from this.

after this is realised, no one will want to provide liquidity, and since the pair cannot be removed or replaced, it will cause denial of service for that token forever.
