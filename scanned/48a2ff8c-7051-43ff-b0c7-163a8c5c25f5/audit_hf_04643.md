# [M] M-07 | Zero Amount Purchases Allowed Before And After Minting Period

## Summary
Severity: Medium
Contest weight: 0.1090
Dataset id: 22382
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Both purchase() and purchaseWithUSDC() do not validate if nftAmount_ parameters is greater than zero. Even though there is no change in the contract state, there will be unexpected events emitted like Transfer, IntervalsReduced and Minted. Furthermore, purchases with zero amounts are possible before startTime and after endTime due to modifier checkAndUpdateReducedIntervals calculating currentIntervalsLeft as zero instead of reverting. Again, although there is no impact of contract state, there could be unexpected behavior with off-chain monitoring systems due to this issue.

## Recommendation
Require that nftAmount_ parameter is non zero in both purchase functions. Also, in checkAndUpdateReducedIntervals revert instead of returning zero if before or after minting period. uint256 currentIntervalsLeft = block.timestamp < startTime || block.timestamp >= endTime ? revert BeforeAfterMintingPeriod() : _initialIntervals - ((block.timestamp - startTime) / interval);
