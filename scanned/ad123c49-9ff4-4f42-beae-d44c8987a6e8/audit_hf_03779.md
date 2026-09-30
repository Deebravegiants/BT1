# [M] Clubs can mint +1 players more than maxGen-

## Summary
Severity: Medium
Contest weight: 0.1051
Dataset id: 19963
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As stated in doc here Initially clubs should be able to mint 10 players. However, clubs can always mint +1 players more than maxGenerationId
An off-by-one error is existed in academy contract when checking the generation ID while minting players. The code currently allows clubs to mint up to maxGenerationId + 1 players, which is inconsistent with the documentation. If clubs send generation IDs in the following sequence: 0-1-2-3-4-5-6-7-8-9-10, all of these numbers will be valid, and the club will be able to mint maxGenerationId + 1 players instead of the intended maxGenerationId
Since this is not intended behaviour according to the protocol docs, I'll label it as high.

## Recommendation
Use generationId >= _maxGenerationId or do not count the "0" index
