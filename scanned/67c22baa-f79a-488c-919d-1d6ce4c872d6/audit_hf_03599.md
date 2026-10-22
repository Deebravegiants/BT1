# [H] ML-1 | Health Score Decreases After Liquidation

## Summary
Severity: High
Contest weight: 0.2876
Dataset id: 19578
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Because each token has a different LTV, a liquidation in a specific token produces a change in borrowing power that is not proportionate to the change in liabilities. As a result, it is easily possible for a position to have a lower health score (become unhealthier) post-liquidation. The position would require more than 1 liquidation at 50% of the liabilities until the health score increased. Consequently, bad debt can stay in the system for a prolonged period and put the protocol at risk of supporting an insolvent position.

- 1000 USDT in liabilities
- 6 ETH each at $100 for 100% LTV ($600 borrowing power)
- 1 BTC each at $400 for 50% LTV ($200 borrowing power)
- Health Factor: ($600 + ($400 * 0.5)) / $1000 = 0.80

Because ETH is the largest position in the portfolio, the ETH will be liquidated.

- 50% of 1000 USDT (liabilities) = 500 USDT
- Proportionate supply = 500 USDT / $100 (ETH price) = 5 ETH
- 500 USDT in liabilities
- 1 ETH in the portfolio ($100 borrowing power)
- 1 BTC in the portfolio ($200 borrowing power)
- New Health Factor: ($100 + ($400 * 0.5)) / $500 = $300 / $500 = 0.60

## Recommendation
Prior to liquidating a position, simulate the health factor post-liquidation. Carefully select the asset to liquidate which will ultimately increase the health factor. Furthermore, consider supporting full liability liquidations. Although this may add complexity as multiple swaps in the portfolio may be needed due to the different supply tokens, it will ensure the borrow position is healthier post-liquidation.
