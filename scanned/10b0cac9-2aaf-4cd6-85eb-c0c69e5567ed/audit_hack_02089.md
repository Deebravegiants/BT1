# [M] 6.2 Staking Formula Differs From Specificaiton

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Specification Changed

The specs define the formula as:

```
stake = k * tokens.
K = (0.07 + 0.93 * (cliffPeriod / 104) ^ 2 + 0.5 * (0.07 + 0.93 * (slopePeriod / 104) ^ 2)).
```
This formula differs from solidity implementation, mostly due to use of following constants:

```
uint256 constant ST_FORMULA_MULTIPLIER = 1081000; //stFormula multiplier = TWO_YEAR_WEEKS^2 * 100
uint256 constant ST_FORMULA_COMPENSATE = 1135050; //stFormula compensate = (0.7+0.35) * ST_FORMULA_MULTIPLIER
uint256 constant ST_FORMULA_SLOPE_MULTIPLIER = 465; //stFormula slope multiplier = 0.93 * 0.5 * 100
uint256 constant ST_FORMULA_CLIFF_MULTIPLIER = 930; //stFormula cliff multiplier = 0.93 * 100
```
- ST_FORMULA_MULTIPLIER should be 1086000 to comply with specs.
- ST_FORMULA_COMPENSATE should be 1135680 to comply with specs.
- ST_FORMULA_SLOPE_MULTIPLIER should be 46.5 to comply with specs.
- ST_FORMULA_CLIFF_MULTIPLIER should be 93 to comply with specs.

Specification corrected:

Specificaion of formula was changed in commit 6167554ff40b7b7f9f6d1ce808fd7d62d04ab3f
to:

```
stake = K * tokens / 1000;
K = ( 11356800 + 9300 * (cliffPeriod)^2 + 4650 * (slopePeriod)^2) / 10816;
```
Code was adjusted in commit 888761566077d51937cf7676417ebe0839f2bdfe implemented
according to this specificaion.
