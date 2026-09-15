# [H] _sendForReceiver is vulnerable to reentrancy. This enables a receiver to drain the remaining fees to distribute. 

## Summary
Severity: High
Chain: Smart contract
Component: 2021-05-nftx
Published: 2021-05-11
Source: https://github.com/code-423n4/2021-05-nftx-findings/issues/68
Type: code-finding

## Details
# Handle

janbro


# Vulnerability details

## Summary
_sendForReceiver is vulnerable to reentrancy. This enables a receiver to drain the remaining fees to distribute. 

## Risk Rating
Critical

## Vulnerability Details
NFTXFeeDistributor.sol

Line 163: (bool success, bytes memory returnData) = address(_receiver.receiver).call(payload);

_sendForReceiver can be reentered before remaining funds are distributed to other receivers through the external call. The `distribute(...)` function on line 48 has no privilege checks and can be subsequently called by a contract that is listed as a receiver.

## Impact
Stolen funds

## Proof of Concept
Given an amount `1,000x10**18` to distribute, a `defaultTreasuryAlloc` of `2x10**17`, an `_receiver.allocPoint` of `2x10**18` and 5 receivers.
In the best case the receiver is in position 0 of the feeReceivers[vaultId] array. Distribute is called, and the malicious receiver contract receives `(1000*10**18) * 2*10**18 / (10*10**18) = 200x10**18`. The malicious contract then calls `donate()` again in their contracts `receiveRewards` callback function and is awarded `(800*10**18-) * 2*10**18 / (10*10**18) = 160x10**18`. Although the treasury will take a fee everytime `distribute()` is called, the attacker can continue to steal funds as long as the balance of the fee distributor is greathr than `_treasuryAlloc` although the default value in this example is negligible. Subsequent `safeTransfer`'s to other receivers do not revert since the amount sent is calculated based on the current balance of the fund, which allows the attacker to leave no funds in the distributor without worrying about the transaction reverting in subsequent transfers. The following equation can be used to determine how much reward can be taken given n steps:

![formula](https://render.githubusercontent.com/render/math?math=%5csum_{n=0}^n%20%5c_tokenBalance%20*%20%5cfrac{%5c_receiver.allocPoint}{%5c_allocTotal}%20*%20(1%20-%20%5cfrac{%5c_receiver.allocPoint}{%5c_allocTotal})^n)

## Tools Used
Manual Code Review

## Recommended Mitigation Steps
Add a reentrancy guard to `_sendForReceiver` to prevent reentrancy due to the external call
