# [H] Wrong address of TWAP contract

## Summary
Severity: High
Reporter: SovaSlava
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L49
Type: audit-issue

## Details
# Wrong address of TWAP contract

## Summary
Wrong address of Uniswap TWAP contract
## Vulnerability Detail
Dca.py has wrong address of uniswap twap contract. 
```solidity
TWAP: constant(address) = 0xFa64f316e627aD8360de2476aF0dD9250018CFc5 
```
Project will plan work on arbitrum network. so check address on arbiscan. https://arbiscan.io/address/0xFa64f316e627aD8360de2476aF0dD9250018CFc5 -> its event not a contract.
## Impact
Users could not call function execute_dca_order(), because this function call _calc_min_amount_out()
```solidity
twap_value: uint256 = Univ3Twap(TWAP).getTwap(_path, _fees, _twap_length)
```
## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L49

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L268
## Tool used

Manual Review

## Recommendation
Change address to correct value.
