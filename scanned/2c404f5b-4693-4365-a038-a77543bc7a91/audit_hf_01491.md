# [M] M-2 Insufﬁcient constraint checks

## Summary
Severity: Medium
Contest weight: 0.2086
Dataset id: 7926
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Insufﬁcient constraint checks increase the human error probability: a platform manager may enter
incorrect data and break the contract logic.
addCollection() (FantiumNFTV1.sol#L266):
• no zero address check for athleteAddress
• no constraint checks for athletePrimarySalesPercentage,
athleteSecondarySalesPercentage
No check for the collectionId existence:
• updateCollectionName (FantiumNFTV1.sol#L297)
• updateCollectionAthleteAddress (FantiumNFTV1.sol#L308)
• toggleCollectionIsPaused (FantiumNFTV1.sol#L319)
• updateCollectionPrice (FantiumNFTV1.sol#L330)
• updateCollectionMaxInvocations (FantiumNFTV1.sol#L342)
• updateCollectionTier (FantiumNFTV1.sol#L353)
• updateCollectionBaseURI (FantiumNFTV1.sol#L366)
• updateCollectionAthleteName (FantiumNFTV1.sol#L378)
• updateCollectionAthletePrimaryMarketRoyaltyPercentage (FantiumNFTV1.sol#L397)
• updateCollectionAthleteSecondaryMarketRoyaltyPercentage (FantiumNFTV1.sol#L422)
No check maxInvocations < ONE_MILLION check:
• updateCollectionMaxInvocations (FantiumNFTV1.sol#L342)
No zero address check:
• updateCollectionAthleteAddress (FantiumNFTV1.sol#L308)
• updateFantiumPrimarySaleAddress (FantiumNFTV1.sol#L467)
• updateFantiumSecondarySaleAddress (FantiumNFTV1.sol#L479)
• updateFantiumMinterAddress (FantiumNFTV1.sol#L508)
• updateFantiumNFTAddress (FantiumMinterV1.sol#L322)
updateTiers (FantiumNFTV1.sol#L493):
• no check for _priceInWei > 0
• no check for maxInvocations < ONEMILLION
fantiumPrimarySalesAddress in getPrimaryRevenueSplits() (FantiumNFTV1.sol#L600) may be
zero. Consider setting it to a non-zero address in the contract's initializer so it is never zero.

## Recommendation
It is recommended to add all necessary checks.
