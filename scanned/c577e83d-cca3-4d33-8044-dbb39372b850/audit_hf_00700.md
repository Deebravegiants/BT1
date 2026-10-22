# [H] H-02 | Users Will Always Pay The Max. Decaying Redemption Fee

## Summary
Severity: High
Contest weight: 0.1821
Dataset id: 2251
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Config.sol, the protocol sets:
uint256 public constant DECAYING_REDEMPTION_FEE_DURATION = 300e18; // 300 seconds, 5 minutes
However, the redemption fee logic in the contract does:
uint256 timePassed = block.timestamp - mintedTimestamp[user];
uint256 percentPassed = timePassed.div(redemptionFeeDuration);
If redemptionFeeDuration is stored as 300e18, then:
• timePassed is a normal integer in seconds (e.g., 150 for half the interval).
• div is a scaled integer division.
• The result becomes 150 ÷ (300 × 10^18) = 0.5 → 0.
Hence, the code incorrectly sees “0% of the duration has passed,” rather than 50%. This breaks the decay logic and always calculates a near‐maximum extra fee.

## Recommendation
Consider setting DECAYING_REDEMPTION_FEE_DURATION to 300 instead of 300e18 in the Config contract.
