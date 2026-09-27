# [M] Hacker can craft malicious 1inch trade to steal the dusted fund in DODORouteProxy.sol

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/26
Type: sherlock-finding

## Details
ctf_sec

medium

# Hacker can craft malicious 1inch trade to steal the dusted fund in DODORouteProxy.sol

## Summary

Hacker can craft malicious 1inch trade to steal the fund in DODORouteProxy.sol

## Vulnerability Detail

In DODORouteProxy.sol, We have the superWithdraw function

```solidity
/// @notice used for emergency, generally there wouldn't be tokens left
function superWithdraw(address token) public onlyOwner {
    if(token != _ETH_ADDRESS_) {
        uint256 restAmount = IERC20(token).universalBalanceOf(address(this));
        IERC20(token).universalTransfer(payable(routeFeeReceiver), restAmount);
    } else {
        uint256 restAmount = address(this).balance;
        payable(routeFeeReceiver).transfer(restAmount);
    }
}
```

as the comment suggest, there may be case if the user's trade has dust balance or user send the token to the contract by mistake. 

But before the admin can step in a withdraw the fund, a hacker can step, craft malicious 1inch trade to steal the fund in DODORouteProxy.sol

The attack vector is enabled by multiple traits of the DODORouteProxy.sol:

1. the 1inch router is whitelisted.

As suggested in the comment above the DODORouteProxy.sol

> ExternalSwap is for other routers like 0x, 1inch and paraswap

2. Unlimited allowance is given in the code.

```solidity
require(isApproveWhiteListedContract[approveTarget], "DODORouteProxy: Not Whitelist Appprove Contract");  

// transfer in fromToken
if (fromToken != _ETH_ADDRESS_) {
    // approve if needed
    if (approveTarget != address(0)) {
        IERC20(fromToken).universalApproveMax(approveTarget, fromTokenAmount);
    }

    IDODOApproveProxy(_DODO_APPROVE_PROXY_).claimTokens(
        fromToken,
        msg.sender,
        address(this),
        fromTokenAmount
    );
}
```

3. 1inch can be used to pull an arbitrary amount of funds from the caller and execute arbitrary call

The design of 1inch's AggregationRouterV4 can be used to pull funds from the DODORouteProxy and execute arbitrary external call:

https://polygonscan.com/address/0x1111111254fb6c44bAC0beD2854e76F90643097d#code#L2309

Please see L2309-2321.

```solidity
if (!srcETH) {
    _permit(address(srcToken), desc.permit);
    srcToken.safeTransferFrom(msg.sender, desc.srcReceiver, desc.amount);
}

{
    bytes memory callData = abi.encodePacked(caller.callBytes.selector, bytes12(0), msg.sender, data);
    // solhint-disable-next-line avoid-low-level-calls
    (bool success, bytes memory result) = address(caller).call{value: msg.value}(callData);
    if (!success) {
        revert(RevertReasonParser.parse(result, "callBytes failed: "));
    }
}
```

4. The low level call data is supplied by user

```sollidity
(bool success, bytes memory result) = swapTarget.call{
    value: fromToken == _ETH_ADDRESS_ ? fromTokenAmount : 0
}(callDataConcat);
```

## Impact

All fund in the contract can be taken before admin can superWithdraw.

## Code Snippet

https://polygonscan.com/address/0x1111111254fb6c44bAC0beD2854e76F90643097d#code#L2309

https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L158-L224

## Tool used

Manual Review

## Recommendation

Make sure no fund is left after the transaction is finished, add balanceOf(address(this)) check to make sure there is no dust amount in the contract.
