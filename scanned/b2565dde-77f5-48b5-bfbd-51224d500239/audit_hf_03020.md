# [H] GLOBAL-4 | Arbitrage Attack

## Summary
Severity: High
Contest weight: 0.1301
Dataset id: 16894
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Documentation in README.md suggests that spot prices from multiple exchanges will be used to determine prices for execution. Such a price collection scheme potentially allows for economically viable price manipulation/arbitrage attacks. Attackers may be able to manipulate prices to game orders into guaranteed profits, or cause mass liquidations.

## Recommendation
Adopt a TWAP with multiple price readings to make such attacks economically unviable. Otherwise, be prepared to use failsafes such as open interest caps to limit these attacks. Optionally, order book depth/liquidity for each exchange should be considered in the calculation to further limit the scope of manipulation attacks.
