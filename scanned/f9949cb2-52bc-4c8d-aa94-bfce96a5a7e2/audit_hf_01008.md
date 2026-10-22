# [M] M-6 Incorrect hardcoded address

## Summary
Severity: Medium
Contest weight: 0.0845
Dataset id: 3449
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During the deployment of SwapExecutorArbitrum two addresses are hardcoded:
• uniswapV3Factory as 0x1F98431c8aD98523631AE4a59f267346ea31F984
• sushiV3Factory as 0xbACEB8eC6b9355Dfc0269C18bac9d6E2Bdc29C4F
SwapExecutorArbitrum.sol#L12
However, the sushiV3Factory address is incorrect as there is no such smart contract deployed on
Arbitrum:
• 0xbACEB8...Bdc29C4F
The correct address is:
• 0x1af415...3D82231e
Sushi Docs:
• https://dev.sushi.com/docs/Products/V3 AMM/Core/Deployment Addresses

## Recommendation
We recommend setting sushiV3Factory either as
0x1af415a1EbA07a4986a52B6f2e7dE7003D82231e or as address(0) if sushiV3Factory is not
going to be used.
