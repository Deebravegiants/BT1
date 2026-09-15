# [C] 6.2 Chainlink Oracle Returns Empty Prices

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Critical Version 1 Code Corrected

ChainlinkOracle maintains the mapping oraclesIndex which stores addresses of chainlink oracles
for each token. The mapping is populated by the admin through the function _addChainlinkOracles:

```
function _addChainlinkOracles(address[] memory tokens, address[] memory oracles) internal {
...
oraclesIndex[token] = oracle;
...
}
```
The function price(token0,token1,safetyIndicesSet) checks if the mapping oraclesIndex
has the addresses for the respective Chainlink oracles:

```
if ((address(chainlinkOracle0) != address(0)) || (address(chainlinkOracle1) != address(0))) {
return (pricesX96, safetyIndices); // returns empty values
}
```
The condition above is incorrect as it returns empty values if the Chainlink oracles exist in the mapping.
This makes the Chainlink oracle - assumed to be the safest by the specifications and the code -
unusable.

Code corrected:

The above check in function price has been revised to return empty prices only if there is no entry for at
least one of the tokens in mapping oraclesIndex:

```
if ((address(chainlinkOracle0) == address(0)) || (address(chainlinkOracle1) == address(0))) {
return (pricesX96, safetyIndices);
}
```
