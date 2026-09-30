# [H] Fees can be charged on a worthless token by exploiting permissionless AMMs

## Summary
Severity: High
Contest weight: 0.4924
Dataset id: 22817
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Due to the permissionless nature of UniV2/UniV3/Balancer, and by the fact that the user is free to choose the input (ETH) or the output token as fees, the Maradona contract can be tricked into receiving a worthless token as fee, effectively allowing the user to bypass any associated fees. The Maradona contract allows for creating multihop trades. While the input token must be ETH, the output token may be any token, and the trader is free to choose whether they want the input token or the output token to serve as protocol fees dit-v1/contracts/Paymaster/Maradona.sol#L288-L290 if (!validateFeeToken(feesTokenAddress, ops)) { revert("Maradona: fee token must be either eth or output token"); } dit-v1/contracts/Paymaster/Maradona.sol#L102-L105 // @dev this function validates if the fee token is either the input or output token, regardless of the type of operation (claim, swap, bridge) function validateFeeToken(address feeTokenAddress, OperationParameters[] memory ops) internal pure returns (bool) { return (feeTokenAddress == address(0) || feeTokenAddress == ops[ops.length - 1].outputToken); } However, because it is permissionless to create an ERC20 token, and create a pool of it on a supported AMM, anyone can create a new pool with their own token/their desired output token, become the sole LP there, and force the protocol into taking their worthless token as fee. This is equivalent to bypassing fee completely. The protocol will receive only worthless tokens as fees, effectively allowing complete fee bypassing.

## Proof of Concept
Alice wants to trade ETH ---> USDC. She can do the following: • Create an ERC20 token PUSH1. This token has no value. • Create a pool on any supported AMM (UniV2/UniV3/Balancer) on the pair PUSH1-USDC, since Alice is the only LP. – It is even possible to create a custom Balancer pool with almost no liquidity at all, and is effectively an Alice-controlled pool. • Trade on the route ETH ---> USDC ---> PUSH1, with the fee token being PUSH1. The first operation is a normal trade, but the second operation is on the newly created pool. – To simulate slippage control on the USDC trade, the PUSH1 token can be an ERC20 token with a transfer hook, that allows Alice to check the USDC output of the trade when the PUSH1 token is inevitably transferred into Maradona. After the trade: • The output token is PUSH1, and the protocol will charge a fee based on that output amount. • The full USDC output from the legit trade is now inside the newly created pool. Because Alice is the sole liquidity provider, she can withdraw all liquidity, and will receive all the output without being subjected to the fee.

## Recommendation
Whitelist a set of tokens to be acceptable as fees. Just be sure to whitelist ETH will be enough to retain all core functionality of Maradona.
