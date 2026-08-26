# [M] M-10 Unmitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-06-xeth-mitigation
Published: 2023-06-20
Source: https://github.com/code-423n4/2023-06-xeth-mitigation-findings/issues/26
Type: code-finding

## Details
# Lines of code




# Vulnerability details

Mitigation of M-10: Issue NOT mitigated

## Mitigated issue
[M-10: First 1 wei deposit can produce lose of user xETH funds in wxETH](https://github.com/code-423n4/2023-05-xeth-findings/issues/3)
Fix: https://github.com/code-423n4/2023-05-xeth/commit/fbb29727ce21857f60c1c94fff43c73b4124a4b4

The issue is similar to the standard inflation attack, except that instead of the attacker's donating tokens directly to the contract to inflate the exchange rate the tokens come from the drip.

## Mitigation review - only a complete theft of the second stake is mitigated
`wxETH.stake()` has been modified to not allow minting of zero shares. This prevents the attack where Alice stakes 1 xETH for 1 wxETH, whereupon the drip inflates the exchange rate to as much as is dripped, and if Bob stakes less than this then <1 wxETH is minted to him, which is rounded down to 0, which implies that Bob lost his stake which is attributed to Alice's 1 share.

The rounding error is still there, however, and may still round down e.g. <2 to 1, which then passes the non-zero mint check.
For example, if Alice first stakes 1 wei, and then 0.101e18 is dripped, the exchange rate is now 0.101e18 wxETH per xETH. Bob stakes 0.2e18 which gives him 0.2e18 / 0.101e18 = 1 wxETH, because of rounding. Now Alice and Bob both own 1 share each, and 0.2e18 + 1 xETH is staked. Alice can then unstake her 1 wxETH for half of the stake, i.e. 0.1e18, which implies a profit for her but a loss for Bob.

### Suggested mitigation steps
A more general version of the non-zero mint check could be employed, namely to only allow exact amounts in terms of minted wxETH to be staked, i.e. only exact multiples of the exchange rate. Then there are no rounding losses.
The downside is that only specific amounts may be staked, in discrete steps which might be large.

The inflation of the exchange rate may in general be avoided by minting dead shares, which mitigation also applies here where the donation comes from the drip.

It is also possible in this particular case to put in place a bound on the drip rate, by making it proportional to the staked amount but at most some maximum drip rate. Then the inflation will be as negligible as the staked amount, which reduces the rounding errors to insignificance.
