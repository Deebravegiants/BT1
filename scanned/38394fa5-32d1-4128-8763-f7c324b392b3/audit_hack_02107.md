# [M] 5.1 Manipulable Price Calculation in

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
AggregateStablePrice Method

```
Security Medium Version 1 Code Partially Corrected
CS-CRVUSD-
```
The price() function in the AggregateStablePrice contract calculates the price of the stablecoin
based on the total supply of stableswap pools.

```
pool_supply: uint256 = price_pair.pool.totalSupply()
```
It is possible to manipulate this value, as a malicious actor could significantly change the total supply of
pools by using a large amount of capital (obtained for example with a flashloan). This manipulation could
alter the computed stablecoin price between the range of the stableswap pool with the lowest price to the
stableswap pool with the greatest price. Given the function's role in determining the price used by the
main price oracle, the pegkeepers, and the monetary policies, this may represent a risk.

Code partially corrected:

The new AggregateStablePrice2 contract implements an exponential moving average over the total
supplies of the pools. Note that the first time the price is calculated in a block is then valid for the
remainder of that block. This means that the price is still manipulable to some extent (e.g. using a
flashloan), although due to the moving average the effect will be reduced. An solution such as using the
last price from the previous block may be a more suitable alternative, however it would require moving
the totalSupply EMA oracle from an external contract to the StableSwap contract.



Here, we list findings that have been resolved during the course of the engagement. Their categories are
explained in the Findings section.

Below we provide a numerical overview of the identified findings, split up by their severity.

```
Critical-Severity Findings 0
```
```
High-Severity Findings 3
```
- Checks-effects-interactions Pattern and Reentrancy Locks Code Corrected
- Incorrect Verification of Health Limit Code Corrected
- Oracle Price Updates Can Be Sandwiched Code Corrected

```
Medium-Severity Findings 6
```
- PegKeeper Can Be Drained if Redeemable Stablecoin Permanently Depegs Code Corrected
- Incorrect Max Band Code Corrected
- Interest Rate Does Not Compound Code Corrected
- Manipulation of Active Band Code Corrected
- Non-Tradable Funds Code Corrected
- Potential Denial of Service (DoS) Attack on Peg Keeper Code Corrected

```
Low-Severity Findings 20
```
- A User's Liquidation Discount Can Be Updated by Anyone at Any Time Code Corrected
- ApplyNewAdmin Event Emitted With Wrong Argument in PegKeeper Code Corrected
- Draining Funds Code Corrected
- Inaccurate _p_oracle_up(n) for High/Low Values of n Code Corrected
- Incorrect Array Length Specification Changed
- Incorrect Calculations in health_calculator Code Corrected
- Incorrect Comments Code Corrected
- Meaningful Revert Reasons Specification Changed
- Missing Sanity Checks Code Corrected
- Multiple Calls to the AMM Code Corrected
- No Events Code Corrected
- Non-Indexed Events Code Corrected
- Potential Optimization With Immutable PriceOracle Code Corrected
- Potentially Incorrect Admin Fees Code Corrected
- Simpler Calculations Possible Code Corrected
- Superfluous Check Code Corrected
- Superfluous Interface Definitions Code Corrected
- Superfluous Variable Assignment for Number of Bands Code Corrected
- Unnecessary Subtraction Code Corrected


- Unused Variables Code Corrected
