# [M] Actual claim rate may be below minClaimRateBips

## Summary
Severity: Medium
Contest weight: 0.4645
Dataset id: 14013
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Assuming minClaimRateBips <= ceilClaimRate, it's possible for minClaimRateBips to not be respected. Consider the following configuration:
• zeroClaimRate = 2500 (25%)
• baseClaimRate = 5000 (50%)
• ceilClaimRate = 8000 (80%)
• baseGasSeconds = 60 (60s)
• ceilGasSeconds = 100 (100s)
Suppose the user has vested 1 ETH over 80s: etherSeconds = 1e18 * 80 = 80e18, etherBalance = 1e18. Assume the user wants to claim at a minClaimRateBips of 6000 (60%). Plugging in the values into the helper contract below,
```solidity
contract Test {
    uint256 public zeroClaimRate = 2500;
    uint256 public baseClaimRate = 5000;
    uint256 public ceilClaimRate = 8000;
    uint256 public baseGasSeconds = 60;
    uint256 public ceilGasSeconds = 100;

    function claimGasAtMinClaimRate(uint256 etherBalance, uint256 secondsStaked, uint256 minClaimRateBips) external view returns (uint256, uint256) {
        uint256 etherSeconds = etherBalance * secondsStaked;
        uint256 bipsDiff = minClaimRateBips - baseClaimRate;
        uint256 secondsDiff = ceilGasSeconds - baseGasSeconds;
        uint256 rateDiff = ceilClaimRate - baseClaimRate;
        uint256 minSecondsStaked = baseGasSeconds + (bipsDiff * secondsDiff / rateDiff);
        uint256 maxEtherClaimable = etherSeconds / minSecondsStaked;
        if (maxEtherClaimable > etherBalance) {
            maxEtherClaimable = etherBalance;
        }
        uint256 secondsToConsume = maxEtherClaimable * minSecondsStaked;
        return getClaimRateBps(secondsToConsume, maxEtherClaimable);
    }

    function getClaimRateBps(uint256 gasSecondsToConsume, uint256 gasToClaim) public view returns (uint256, uint256) {
        uint256 secondsStaked = gasSecondsToConsume / gasToClaim;
        if (secondsStaked < baseGasSeconds) {
            return (zeroClaimRate, 0);
        }
        if (secondsStaked > ceilGasSeconds) {
            uint256 gasToConsumeNormalized = gasToClaim * ceilGasSeconds;
            return (ceilClaimRate, gasToConsumeNormalized);
        }
        uint256 rateDiff = ceilClaimRate - baseClaimRate;
        uint256 secondsDiff = ceilGasSeconds - baseGasSeconds;
        uint256 secondsStakedDiff = secondsStaked - baseGasSeconds;
        uint256 additionalClaimRate = rateDiff * secondsStakedDiff / secondsDiff;
        uint256 claimRate = baseClaimRate + additionalClaimRate;
        return (claimRate, gasSecondsToConsume);
    }
}
```
the resultant claim rate is 5975, which is less than the expected minimum claim rate of 6000.

## Recommendation
Consider using OpenZeppelin Math's ceilDiv for the calculation of minSecondsStaked to consume more etherSeconds to fulfil the minimum requested claim rate.
- uint256 minSecondsStaked = baseGasSeconds + (bipsDiff * secondsDiff / rateDiff);
+ uint256 minSecondsStaked = baseGasSeconds + ceilDiv(bipsDiff * secondsDiff, rateDiff);
