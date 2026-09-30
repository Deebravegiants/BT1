# [H] Commit-reveal does not sufficiently protect againstslash frontrunnings

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23284
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Description: A commit-reveal scheme in RLN to battle the case where a slasher frontruns another by using the provided private key, but setting up his own reward recipient address. It works in the following 2-step way:
1. Commit a hash.
2. Reveal the private key and rewards address corresponding to that hash. In step 2, the actual slash happens. However, this protection is insufficient as instead of the usual case where the attacker would frontrun the slash directly, he can simply frontrun the reveal by seeing the private key then.

## Recommendation
Recommended Mitigation: Make slash() internal so only commit-reveal way of slashing is available. The other option is to only make slash() available to call when no commit slash has been made.
