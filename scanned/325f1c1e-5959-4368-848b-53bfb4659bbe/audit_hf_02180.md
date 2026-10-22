# [M] Improper Logic of Mining::getDateTimeConcat()

## Summary
Severity: Medium
Contest weight: 0.4272
Dataset id: 12163
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
By design, the Mining contract is one of the main entries, which implements an incentive mechanism that rewards the miners with the rewardToken token. In particular, mapping(uint256 => uint256) public rewardSharesByDays is designed to store the pool's accRewardPerShare per day. Meanwhile, the getDateTimeConcat() routine is used to generate the key of the rewardSharesByDays mapping. While examining its logic, we observe there is an improper implementation that needs to be improved.
To elaborate, we show below the related code snippet of the Mining contract.
Inside the getDateTimeConcat() routine, the formula of uint256 date = (year * 1000) + (month * 100) + day (line 410) is designed to generate the key of the rewardSharesByDays mapping to represent one day uniquely.
However, after further analysis, we observe different days may generate the same key (e.g., 2022 * 1000 + 11 * 100 + 1 == 2023 * 1000 + 1 * 100 + 1), which directly undermines the assumption of the design. Given this, we suggest to improve the formula as below: uint256 date = (year * 10000) + (month * 100) + day (line 410).
```solidity
function getDateTimeConcat(uint256 _timestamp) public pure returns (uint256) {
    (uint256 year, uint256 month, uint256 day) = DateTime.timestampToDate(_timestamp);
    uint256 date = (year * 1000) + (month * 100) + day;
    return date;
}
```

## Recommendation
Correct the implementation of the getDateTimeConcat() routine as above-mentioned.
