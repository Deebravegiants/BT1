# [H] GLOBAL-3 | Lack of Open Interest Caps

## Summary
Severity: High
Contest weight: 0.1810
Dataset id: 17857
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There is a lack of general open interest caps per MarketToken aside from the reserves validation. This enables users to open positions and increase the open interest right up to the reserve limit so that anyone attempting to withdraw from the MarketToken (or possibly swap with this MarketToken) will be unable to pass validateReserves. This way depositors funds can be held hostage – only being freed if others deposit (at which point someone may increase the open interest yet again and hold these new funds hostage as well). Additionally, in the event of arbitrage attacks the exchange has no effective mechanism to limit the open interest per market to limit the attack size.

## Recommendation
Implement open interest caps that limit the total open interest a MarketToken can have for either direction.
