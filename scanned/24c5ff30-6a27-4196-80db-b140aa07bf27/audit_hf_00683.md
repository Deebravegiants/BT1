# [M] `msg.value` is Sent Multiple times When Performing a Swap

## Summary
Severity: Medium
Contest weight: 0.6190
Dataset id: 2224
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[LibSwap.sol#L42](https://github.com/code-423n4/2022-03-lifinance/blob/main/src/Libraries/LibSwap.sol#L42)  
[Swapper.sol#L12-L23](https://github.com/code-423n4/2022-03-lifinance/blob/main/src/Facets/Swapper.sol#L12-L23)  

`msg.value` is attached multiple times to external swap calls in `LibSwap.swap()`.

If `Swapper._executeSwaps()` is called with the native token as the `swapData.fromAssetId` more than once and `msg.value > 0` then more value will be transferred out of the contract than is received since `msg.value` will be transferred out `_swapData.length` times.

The impact is that the contract can have all the native token balance drained by an attacker who has makes repeated swap calls from the native token into any other ERC20 token. Each time the original `msg.value` of the sender will be swapped out of the contract. This attack essentially gives the attacker `_swapData.length * msg.value` worth of native tokens (swapped into another ERC20) when they should only get `msg.value`.

## Proof of Concept
`Swapper._executeSwaps()` iterates over a list of `SwapData` calling `LibSwap.swap()` each time (note this is an internal call).

```solidity
function _executeSwaps(LiFiData memory _lifiData, LibSwap.SwapData[] calldata _swapData) internal {
    // Swap
    for (uint8 i; i < _swapData.length; i++) {
        require(
            ls.dexWhitelist[_swapData[i].approveTo] == true && ls.dexWhitelist[_swapData[i].callTo] == true,
            "Contract call not allowed!"
        );

        LibSwap.swap(_lifiData.transactionId, _swapData[i]);
    }
}
```

Inside `LibSwap.swap()` we make an external call to `_swapData.callTo` with `value : msg.value`. Due to the loop in `Swapper._executeSwaps()` this repeatedly sends the original `msg.value` in the external call.

```solidity
(bool success, bytes memory res) = _swapData.callTo.call{ value: msg.value }(_swapData.callData);
```

## Recommendation
This issue may be mitigated by only allowing `fromAssetId` to be the native token once in `_swapData` in `Swapper._executeSwaps()`. If it occurs more than once the transaction should revert.

We are aware that the contract allows users to use latent funds, although we disagree on it being an issue as no funds (ERC20 or native) should ever lay in the contract. To make sure that no value is ever kept by the diamond, we now provide refunds for outstanding user value (after bridges/swaps). 

Adjusting this as Medium Risk. There can be fund leftover in the contract under normal operation, for example [this tx](https://etherscan.io/tx/0xe78c36dd2c2f21cade00a4099701b9c9f82acc8da568e1048a4d7287ce2e45b0). In fact, ~$300 worth of token is left in the LI.Fi smart contract on ETH mainnet [0x5a9fd7c39a6c488e715437d7b1f3c823d5596ed1](https://etherscan.io/address/0x5a9fd7c39a6c488e715437d7b1f3c823d5596ed1) as of block 14597316. I don’t think this is High Risk because the max amount lost is no more than allowed slippage, which can be loss to MEV too. Not a duplicate of M-02 since `msg.value` is the vector here.

This has been fixed in the most recent version of `src/Helpers/Swapper.sol` which sweeps any latent funds back to the user’s wallet.
