# [H] H-03 | Insolvency Because Of tradeRatio Rounding

## Summary
Severity: High
Contest weight: 0.2873
Dataset id: 1981
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When _quoteOrTrade is called and PnL is calculated, the tradeRatio experiences precision loss because of rounding down when performing divDecimal. While this is fine for longs, it's not for shorts. That's because the tradeRatio is a fill price and if the fill price is lower, shorts will have made a profit. In result, when the PnL for shorts is calculated the trader will experience a smaller loss, leaving the system with fewer funds available than it should have in order to operate. This can be most visible if a position has only borrowedVGas (short) and makes a trade to close the position. Because the entirety of the debt is being paid off, it would be expected that the vEthToZero would at least match the runtime.tradedVEth. However, the vEthToZero would be slightly less due to the tradeRatioD18 rounding, and less collateral being held in the Foil contract. Later, when LPs try to close or settle their position, they will not be able to do so. The contract will try to send them the amount they have earned, but this amount is not fully backed by the losses of the traders and the transaction will revert with ERC20: transfer amount exceeds balance.

## Proof of Concept
https://github.com/GuardianAudits/foil-fuzzing/commit/c474aa3613df97c83793af92b37be0c29a653562

## Recommendation
In case of a short position, round the tradeRatio up to provide a worse fill price when going towards the long direction.
