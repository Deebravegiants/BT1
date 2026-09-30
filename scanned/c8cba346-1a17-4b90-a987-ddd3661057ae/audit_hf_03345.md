# [C] CON-1 | _validateRange Prevents Critical Values Being Set

## Summary
Severity: Critical
Contest weight: 0.1162
Dataset id: 18196
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _validateRange function does not perform any validation on the value, but rather reverts for specific keys such as the Keys.SWAP_FEE_FACTOR and Keys.POSITION_FEE_FACTOR. This restricts the protocol from setting these crucial values for the exchange.

## Proof of Concept
https://github.com/GuardianAudits/GMX_3/blob/main/test/Guardian/PoCs/CON-1.ts

## Recommendation
Update the _validateRange function to perform validation on the value being passed rather than simply reverting for certain keys.
