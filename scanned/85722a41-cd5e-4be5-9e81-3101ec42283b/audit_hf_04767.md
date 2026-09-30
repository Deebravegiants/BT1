# [H] Malicious Data Injection via

## Summary
Severity: High
Contest weight: 0.2578
Dataset id: 22612
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
deactivate() and liquidate() functions as well as withdrawLender and withdrawBorrower functions allow attacker to inject malicious bytes calldata data. This specifically pertains to the execution of multicall in the Teahouse Liquidity Warehouse extension, where malicious swap data can lead to adverse swaps via uniswapV3Swap, resulting in a drain of assets. The TeahouseLiquidityWarehouse contract facilitates interactions through multicall, which includes swap operations. Malicious actors can exploit the deactivate() or liquidate() functions by passing in crafted swapData that triggers detrimental swaps, draining assets without the protocol receiving the intended swap outcomes. This vulnerability stems from the lack of validation on the swapData passed into multicall, which can include calls to uniswapV3Swap with specifically crafted parameters. This vulnerability will lead to significant financial losses by enabling attackers to execute swaps that deplete the protocol's assets without receiving fair value in return.

## Recommendation
It is recommended to implement robust validation mechanisms for swapData before its execution within multicall. This could include checks on the legitimacy of swap paths, slippage rates, and the authenticity of pool addresses to ensure they align with expected parameters and are not detrimental to the protocol.
