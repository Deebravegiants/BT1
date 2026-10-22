# [M] ETH item purchases can be DOSed

## Summary
Severity: Medium
Contest weight: 0.3822
Dataset id: 3112
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Function buyItemWithETH() uses the spot price directly (adhering to a certain deviation). If the deviation exceeds the set percentage, we revert. The issue is that an attacker can intentionally manipulate the spot price, forcing the buyer's call to revert due to the deviation. Other than being a DOS issue, an attacker could potentially create a market around this by providing services to specific users to receive listed rare/legendary NFTs as a guarantee.
```solidity
uint256 spotPrice = getSpotPrice();
checkIsDeviationOutOfBounds(spotPrice);
```

## Recommendation
Consider using the TWAP price directly instead of the existing spot price and twap price deviation system.
