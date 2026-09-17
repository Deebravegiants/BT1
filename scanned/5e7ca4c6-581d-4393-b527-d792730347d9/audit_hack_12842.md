# [M] Wrong hardcoded TWAP address

## Summary
Severity: Medium
Reporter: Tricko
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L49
Type: audit-issue

## Details
# Wrong hardcoded TWAP address

## Summary
The `DCA.vy` contract is using the wrong hardcoded `TWAP` address, making impossible for DCA orders to be executed.

## Vulnerability Detail
As shown in the code snippet from the function `_calc_min_amount_out`, it calls the method `getTwap` of the `Univ3Twap` contract, but the `TWAP` constant address defined in `Dca.vy` is not from any deployed contract in the Arbitrum network (https://arbiscan.io/address/0xFa64f316e627aD8360de2476aF0dD9250018CFc5).

```solidity
token_in_decimals: uint256 = convert(ERC20Detailed(_path[0]).decimals(), uint256)
twap_value: uint256 = Univ3Twap(TWAP).getTwap(_path, _fees, _twap_length)
```
If `Dca.vy` is deployed in its current state, the primary function of executing DCA orders will not be available. This is because any calls to `Univ3Twap(TWAP).getTwap(_path, _fees, _twap_length)` with the incorrect `TWAP` address will revert, rendering the execution of DCA orders impossible.

## Impact
It will be impossible to execute any DCA order, as every call to `execute_dca_order` will revert as explained above. Therefore completely blocking this functionality of the Spot DEX.

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L49

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L253-L276

## Tool used
Manual Review

## Recommendation
Use the correct TWAP contract address.
