# [M] M-01 | NoToken Cap May Be Exceeded During Minting

## Summary
Severity: Medium
Contest weight: 0.0988
Dataset id: 2293
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The mint function enforces the yesNoTokenCap, but it only checks the supply of Yes tokens.
This creates a potential issue where the supply of No tokens can exceed the cap if there is an
imbalance between the total supply of Yes and No tokens.
This imbalance can occur because Yes tokens can be burned (since YesNoToken is an
ERC20Burnable contract).
For example:
• yesNoTokenCap = 100
• Initial supply: Yes = 90, No = 90
• A user burns 10 Yes tokens, reducing the Yes supply to 80.
• The same user mints 20 Yes tokens, bringing the Yes supply back to 100.
• The final supply becomes: Yes = 100, No = 110, exceeding the cap.

## Recommendation
Check that the No token supply does not exceed the yesNoTokenCap during minting.
