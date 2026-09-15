# [H] calldata is not validated meaning an attacker can call arbitrary calldata to make reentrancy  or steal funds

## Summary
Severity: High
Reporter: simon135
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L205
Type: audit-issue

## Details
# calldata is not validated meaning an attacker can call arbitrary calldata to make reentrancy  or steal funds

## Summary
Calldata is not validated meaning an attacker can call arbitrary calldata to make reentrancy or steal funds/get out of fees . When calldata bytes are not validated you can do arbitrary operations that  shouldn't be done.
## Vulnerability Detail
When we are swaping tokens  The attacker calls swapTarget with arbitrary `callDataConcat` which then they can use to reenter or do another operation with that calldata to call some contract. 
From a user perspective if calldata is not validated then a user can call a swap target that can't handle the `callDataConcat` and the function will revert.
## Impact
An attacker can swap a lot more  in the swap target than the  function knows and then the attacker doesn't have  to pay as much in fees
steps:
attacker transfers 5 eth
but in the swapTarget they swap 6 ether  then they get out of paying  more fees 
but also if they swap less then  users can loose funds and pay to much fees 
## Code Snippet
```solidity 
{
            require(swapTarget != _DODO_APPROVE_PROXY_, "DODORouteProxy: Risk Target");
            (bool success, bytes memory result) = swapTarget.call{
                value: fromToken == _ETH_ADDRESS_ ? fromTokenAmount : 0
            }(callDataConcat);
            // revert with lowlevel info
            if (success == false) {
                assembly {
                    revert(add(result,32),mload(result))
                }
            }
        }

```
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L205
## Tool used

Manual Review

## Recommendation
decode the data and go through some sort of input validation or make sure that the `swapTarget` can handle that calldata or that it doesn't revert.
