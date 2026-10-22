# [M] Possible Integer Overflow  on smart-contract-EVM/src/oracle/OracleAdaptorWstETH.sol

## Summary
Severity: Medium
Reporter: Decent Gingham Bear
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# Possible Integer Overflow  on smart-contract-EVM/src/oracle/OracleAdaptorWstETH.sol

## Summary
Possiblility to make a Integer Overflow

## Vulnerability Detail

No checks for integer overflows and underflows in price calculations.

## Impact
Incorrect token pricing, economic exploits.

## Code Snippet

``` solidity
uint256 tokenPrice = ((SafeCast.toUint256(price) 
  * SafeCast.toUint256(ETHPrice)) / Types.ONE) / 1e8;
```
  
## Tool used

Manual Review

## Recommendation

Use OpenZeppelin SafeMath for overflow protection:

``` solidity
using SafeMath for uint256;

uint256 tokenPrice = (price.toUint256().mul(ETHPrice))
  .div(Types.ONE.mul(1e8));
```
