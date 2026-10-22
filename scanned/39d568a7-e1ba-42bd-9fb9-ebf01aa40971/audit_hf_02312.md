# [M] Incompatibility with Deflationary Tokens

## Summary
Severity: Medium
Contest weight: 0.4625
Dataset id: 12596
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In OneSwap, the OneSwapRouter contract is designed to be the main entry for interaction with trading users. In particular, one entry routine, i.e., swapToken(), accepts asset transfer-in and swaps it for another. Naturally, the contract implements a number of low-level helper routines to transfer assets into or out of OneSwap. These asset-transferring routines work as expected with standard ERC20 tokens: namely the vault's internal asset balances are always consistent with actual token balances maintained in individual ERC20 token contract.

```solidity
function _swap(address input, uint amountIn, address[] memory path, address _to) internal virtual returns (uint[] memory amounts) {
    amounts = new uint[](path.length + 1);
    amounts[0] = amountIn;
    for (uint i = 0; i < path.length; i++) {
        (address to, bool isLastSwap) = i < path.length - 1 ? (path[i + 1], false) : (_to, true);
        amounts[i + 1] = IOneSwapPair(path[i]).addMarketOrder(input, to, uint112(amounts[i]), isLastSwap);
        if (!isLastSwap) {
            (address stock, address money) = _getTokensFromPair(path[i]);
            input = (stock == input) ? stock : money;
        }
    }
}

function swapToken(address token, uint amountIn, uint amountOutMin, address[] calldata path, address to, uint deadline) external override ensure(deadline) returns (uint[] memory amounts) {
    require(path.length >= 1, "OneSwapRouter: INVALID_PATH");
    // ensure pair exist
    _getTokensFromPair(path[0]);
    _safeTransferFrom(token, msg.sender, path[0], amountIn);
    amounts = _swap(token, amountIn, path, to);
    require(amounts[path.length] >= amountOutMin, "OneSwapRouter: INSUFFICIENT_OUTPUT_AMOUNT");
}
```

However, there exist other ERC20 tokens that may make certain customization to their ERC20 contracts. One type of these tokens is deflationary tokens that charge certain fee for every transfer or transferFrom. As a result, this may not meet the assumption behind these low-level asset-transferring routines.

In other words, the above operations, such as swapToken(), may introduce unexpected balance inconsistencies when comparing internal asset records with external ERC20 token contracts. Apparently, these balance inconsistencies are damaging to accurate and precise portfolio management of OneSwap and affects protocol-wide operation and maintenance.

A similar issue can also be found in SupervisedSend. One possible mitigation is to measure the asset change right before and after the asset-transferring routines. In other words, instead of bluntly assuming the amount parameter in transfer or transferFrom will always result in full transfer, we need to ensure the increased or decreased amount in the pool before and after the transfer or transferFrom is expected and aligned well with our operation. Though these additional checks cost additional gas usage, we consider they are necessary to deal with deflationary tokens or other customized ones if their support is deemed necessary.

Another mitigation is to regulate the set of ERC20 tokens that are permitted into OneSwap for indexing. However, as a trustless intermediary, OneSwap may not be in the position to effectively regulate the entire process. Meanwhile, there exist certain assets that may exhibit control switches that can be dynamically exercised to convert into deflationary.

We need to point out that this issue can be traced back to the Periphery codebase of UniswapV2.

## Recommendation
To accommodate the support of possible deflationary tokens, it is better to check the balance before and after the transferFrom() call to ensure the book-keeping amount is accurate. This support may bring additional gas cost.
