# [M] M-02 | Price Impact Sandwich Attack

## Summary
Severity: Medium
Contest weight: 0.0742
Dataset id: 22107
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users who balance the skew can be sandwiched by an attacker who front runs and back runs the
call:
• The skew is at 1000
• The user tries to balance the skew by shorting -1000
• Attacker front runs the call and shorts -1000 (receives a positive price impact)
• User call goes through and the user imbalances the skew by -1000 (receives a negative price
impact)
• Attacker back runs the call and longs 1000 (receives a positive price impact)

## Recommendation
Inform users about the risk of this attack so the slippage checks are set accordingly.
