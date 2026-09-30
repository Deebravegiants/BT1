# [H] Missing accumulatedFee debit on the paying side may make the product insolvent.

## Summary
Severity: High
Contest weight: 0.2939
Dataset id: 17394
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The platform/product fee (accumulatedFee) component of the funding fee (accumulatedFunding) is missing a debit on the paying side. The current implementation does not debit the platform/product fee accumulatedFee on the paying side. Given: Example scenario: Alice is the only Maker of the product, holding a position of 20 with a collateral of 100; Bob is the only Taker, holding a position of 10 with a collateral of 100; rateAccumulated = 10%; The price is 10; product.total = 200; FundingFeeRate is 0.1 (10%); In product.settle(): takerNotional = 10 * 10 == 100; fundingAccumulated = 100 * 10% == 10; accumulatedFee = 10 * 0.1 == 1; fundingIncludingFee = +(10-1) == 9; Total accumulatedFunding on the maker side is 9; total accumulatedFunding on the taker side is -9; As a result: product.total = 199; Alice's account = 100+9 == 109; Bob's account = 100-9 == 91; The product is now insolvent as the total liabilities is 109 + 91 == 200, but the total assets is only 199. The product will become insolvent right after the product is settled because the accumulatedFee will be deducted from the total assets (product.total) but the total liabilities (sum of all takers and makers' product accounts) remain unchanged. In other words, a fee is taken from the product but no one is paying for that.

## Recommendation
Add below to the end of function _accumulateFunding: if (fundingAccumulated.sign() == -1) { accumulatedFunding.maker = accumulatedFunding.maker.sub(accumulatedFee); } else {accumulatedFunding.taker = accumulatedFunding.taker.sub(accumulatedFee);}
