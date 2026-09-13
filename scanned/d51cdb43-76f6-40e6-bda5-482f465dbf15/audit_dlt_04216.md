# [H] swapTarget in ExternalSwap does not block DODOApprove.sol address

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/30
Type: sherlock-finding

## Details
ctf_sec

high

# swapTarget in ExternalSwap does not block DODOApprove.sol address

## Summary

swapTarget in ExternalSwap does not block DODOApprove.sol address

## Vulnerability Detail

The function external swap allows the user to swap on external proxies such as 1inch, paraswap and 0x.

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

the code check swapTarget != _DODO_APPROVE_PROXY,

but the code does not check swapTarge != DODOApprove. 

there is a function in claimTokens in DODOApprove.

```solidity
function claimTokens(
    address token,
    address who,
    address dest,
    uint256 amount
) external {
    require(msg.sender == _DODO_PROXY_, "DODOApprove:Access restricted");
    if (amount > 0) {
        IERC20(token).safeTransferFrom(who, dest, amount);
    }
}
```

then the hacker can craft order to call DODOApprove#claimToken to drain the fund from user that give allowance to the contract DODOApprove.

## Impact

Fund from the user that give allowance to DODOApprove can be drained.

## Code Snippet

https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L200-L213

## Tool used

Manual Review

## Recommendation

We recommend the project check the swapTarget not equal to DODOApprove
