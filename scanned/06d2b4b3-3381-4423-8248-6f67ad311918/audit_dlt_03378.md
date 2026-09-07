# [M] Unauthorized functions in Ladle.sol and PoolRouter.sol

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-05-yield
Published: 2021-05-30
Source: https://github.com/code-423n4/2021-05-yield-findings/issues/6
Type: code-finding

## Details
# Handle

gpersoon


# Vulnerability details

## Impact
Both Ladle.sol and PoolRouter.sol contain a function batch, which gives access to several internal functions.
Some of those functions call functions in other contracts which have an "auth" access control mechanism.
However several internal functions can just be executed without any additional checks. These include the functions:
//  https://github.com/code-423n4/2021-05-yield/blob/main/contracts/Ladle.sol
_retrieve,  _forwardPermit, _forwardDaiPermit, _joinEther, _exitEther, _transferToPool, _route, _transferToFYToken, _redeem, _moduleCall
// https://github.com/code-423n4/2021-05-yield/blob/main/contracts/yieldspace/PoolRouter.sol#L162
_route._transferToPool._forwardPermit._forwardDaiPermit._joinEther.

The most risky functions seem to be: _redeem, _exitEther and _moduleCall
_redeem and _exitEther allow the transfer of tokens and eth out of the Ladle.sol and PoolRouter.sol contract.
_moduleCall allows for arbitrary calls to external modules.

## Proof of Concept
https://github.com/code-423n4/2021-05-yield/blob/main/contracts/Ladle.sol#L539
function batch(Operation[] calldata operations, bytes[] calldata data) external payable {
... 
          _exitEther(payable(to));

 function _exitEther(address payable to)  private returns (uint256 ethTransferred)
    {
        ethTransferred = weth.balanceOf(address(this));
        weth.withdraw(ethTransferred);   // TODO: Test gas savings using WETH10 `withdrawTo`
        to.safeTransferETH(ethTransferred);
    }

// https://github.com/code-423n4/2021-05-yield/blob/main/contracts/yieldspace/PoolRouter.sol#L162
 function batch( PoolDataTypes.Operation[] calldata operations,bytes[] calldata data) external payable {
   ....
  _exitEther(to);


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2021-05-yield-findings/issues/6_
