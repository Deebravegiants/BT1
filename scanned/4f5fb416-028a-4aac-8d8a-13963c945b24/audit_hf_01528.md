# [M] RubiconMarketAddress in BathPair can’t be updated

## Summary
Severity: Medium
Contest weight: 0.0893
Dataset id: 8133
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
RubiconMarketAddress in BathPair is initialized only once:
    
    RubiconMarketAddress = IBathHouse(_bathHouse).getMarket();

but market can change in Bath house:
    
    /// @notice Admin-only function to set a Bath Token's target Rubicon Market
    function setMarket(address newMarket) external onlyAdmin {
        RubiconMarketAddress = newMarket;
    }

Thus it will get out of sync. Also, the comment says that it changes Bath Token’s target Rubicon market but actually it updates its own instance variable.

## Recommendation
I think RubiconMarketAddress should sync between BathPair and BathHouse.

Not needed in practice.

Issue stands because there’s a non-zero possibility of it happening.
