# [M]  `getUnderlyingPrice()` should return `0` when errored

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-canto
Published: 2022-09-08
Source: https://github.com/code-423n4/2022-09-canto-findings/issues/93
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-09-canto/blob/65fbb8b9de22cf8f8f3d742b38b4be41ee35c468/src/Swap/BaseV1-periphery.sol#L487-L522


# Vulnerability details

## Impact

The `Comptroller` is expecting `oracle.getUnderlyingPrice` to return `0` for errors (Compound style returns, no revert). The current implementation will throw errors, resulting in the consumer of the oracle getting unexpected errors.

## Proof of Concept

```solidity
function getUnderlyingPrice(CToken ctoken) external override view returns(uint) {
         address underlying;
        { //manual scope to pop symbol off of stack
        string memory symbol = ctoken.symbol();
        if (compareStrings(symbol, "cCANTO")) {
            underlying = address(wcanto);
            return getPriceNote(address(wcanto), false);
        } else {
            underlying = address(ICErc20(address(ctoken)).underlying()); // We are getting the price for a CErc20 lending market
        }
        //set price statically to 1 when the Comptroller is retrieving Price
        if (compareStrings(symbol, "cNOTE")) { // note in terms of note will always be 1 
            return 1e18; // Stable coins supported by the lending market are instantiated by governance and their price will always be 1 note
        } 
        else if (compareStrings(symbol, "cUSDT") && (msg.sender == Comptroller )) {
            uint decimals = erc20(underlying).decimals();
            return 1e18 * 1e18 / (10 ** decimals); //Scale Price as a mantissa to maintain precision in comptroller
        } 
        else if (compareStrings(symbol, "cUSDC") && (msg.sender == Comptroller)) {
            uint decimals = erc20(underlying).decimals();
            return 1e18 * 1e18 / (10 ** decimals); //Scale Price as a mantissa to maintain precision in comptroller
        }
        }
        
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-09-canto-findings/issues/93_
