# [M] Unchecked transfer result of ERC20 tokens

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/42
Type: sherlock-finding

## Details
zimu

high

# Unchecked transfer result of ERC20 tokens

## Summary
The return value of an external transfer call is not checked in DODORouteProxy._multiSwap. Some tokens do not revert in case of failure and return false. 

## Vulnerability Detail
Line 420 and 423 donot check the return value of IERC20(...).transfer(...). Once the token called implements transfer without revert when failure, the funds would lose：

    if (curPoolInfo.poolEdition == 1) {
        //For using transferFrom pool (like dodoV1, Curve), pool call transferFrom function to get tokens from adapter
        IERC20(midToken[i]).transfer(curPoolInfo.adapter, curAmount);
    } else {
        //For using transfer pool (like dodoV2), pool determine swapAmount through balanceOf(Token) - reserve
        IERC20(midToken[i]).transfer(curPoolInfo.pool, curAmount);
    }

## Impact
High. It would cause the lost of  fund of users.

## Code Snippet
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol?plain=1#L387

    DODORouteProxy._multiSwap(address[],uint256[],bytes[],address[]) (contracts/SmartRoute/DODORouteProxy.sol#387-442) ignores return value by IERC20(midToken[i]).transfer(curPoolInfo.adapter,curAmount) (contracts/SmartRoute/DODORouteProxy.sol#420&#423)

## Tool used

Manual Review

## Recommendation
Check if the IERC20(...).transfer(...) return False
