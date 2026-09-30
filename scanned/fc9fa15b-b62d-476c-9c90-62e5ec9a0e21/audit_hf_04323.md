# [H] H-02 | Slide Allows Anchor To Exceed Discovery

## Summary
Severity: High
Contest weight: 0.1546
Dataset id: 21479
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When removing and adding back liquidity to the anchor position in the slide function, the anchorReserves are tracked and added back to the adjusted anchor position.
However the anchor position has moved leftwards after the slide, therefore the liquidity for the anchor position will increase as the reserves are maintained.
As a result, since the new discovery liquidity cannot increase past the old discovery liquidity, the protocol can enter a state where the anchor liquidity is greater than the discovery liquidity.

## Recommendation
Consider the following resolution options:
• No longer require the new discoveryL ≤ old discoveryL
• Switch back to maintaining the liquidity for the anchor, rather than the reserves
