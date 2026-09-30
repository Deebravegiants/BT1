# [C] PPU-1 | Open Interest Value Uninitialized

## Summary
Severity: Critical
Contest weight: 0.1318
Dataset id: 18153
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the getNextOpenInterestParams function the nextLongOpenInterest and nextShortOpenInterest variables are not initialized from the default values and only one is set in either of the params.isLong cases. This drastically misrepresents the open interest balance of the market and yields nonsensical price impact calculations.

## Proof of Concept
https://github.com/GuardianAudits/GMX_3/blob/main/test/Guardian/PoCs/PPU_1.ts

## Recommendation
Initialize each of the nextLongOpenInterest and nextShortOpenInterest values to the current open interest on each side.
