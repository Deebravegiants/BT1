# [H] Unsafe Listing of KlayswapUsdtUsdc LPs

## Summary
Severity: High
Contest weight: 0.1943
Dataset id: 13016
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned earlier, the Shoebill protocol is heavily forked from the popular AaveV2 protocol. However, the use of KlayswapUsdtUsdcVault shows the support of Klayswap-based LP tokens as the collateral. Our analysis shows the potential incompatibility of current AaveV2-based protocols with Klayswap-based LP tokens. In particular, the discussion with the team indicates the Fair Uniswap s LP Token Pricing model will be used as the backend oracle. Unfortunately, the known Fair Uniswap s LP Token Pricing is not compatible with the AaveV2-based lending protocols. The reason is that the fair LP price approach may be manipulated via donation to inﬂate the LP valuation, which is further combined with leverage to drain pool funds!

## Recommendation
Revisit the support of Klayswap-based LP tokens as the collateral. Or make use of reliable oﬀ-chain price oracles for robust feed of LP token prices.
