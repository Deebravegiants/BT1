# [M] Proper Logic In SLDBroker::calcBrokerAmount()

## Summary
Severity: Medium
Contest weight: 0.4597
Dataset id: 12993
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
To lower the barrier for protocol users, the Shield protocol has the support of so-called brokers. Implemented in the SLDBroker contract, the brokers can be ranked and incentivized to better engage protocol users. While reviewing the broker support, we notice an internal function needs to be improved.

To elaborate, we show below this function, i.e., calcBrokerAmount(). As the name indicates, this function is designed for calculating ranks and rewards for brokers. However, the calculation for the USDT-related rewards mistakenly uses the entire trading volume as the reward without taking into account the proper level-speciﬁc RewardNumerator. As a result, current brokers at the ranking level B will received more rewards than expected, at the potential loss of other protocol brokers!
```solidity
function calcBrokerAmount(
    address _broker,
    uint256 _tokenType,
    uint256 _amount
) internal {
    // current ranking for broker
    uint256 originalRating = brokersRating[_broker];
    brokerInvitedAmount[_broker] = brokerInvitedAmount[_broker].add(
        _amount
    );
    uint256 index;
    index = (originalRating > BROKERSLENGTH)
    ? (BROKERSLENGTH)
    : (originalRating - 1);
    for (uint256 i = index; i > 0; i--) {
        if (
            brokerInvitedAmount[_broker] <=
            brokerInvitedAmount[brokersRatingList[i - 1]]
        ) {
            break;
        }
        // swap adjacent rankings
        address tmpPriviousBroker = brokersRatingList[i - 1];
        (brokersRating[tmpPriviousBroker],
        brokersRating[_broker],
        brokersRatingList[i],
        brokersRatingList[i - 1]
        ) = (i + 1, i, tmpPriviousBroker, _broker);
    }
    uint256 currentRating = brokersRating[_broker];
    if (currentRating <= BROKERSRATINGA) {
        // Ranking Level A
        uint256 rewards = _amount.mul(LevelARewardNumerator).div(
            RewardPortionDenominator
        );
        brokersRewards[_broker][_tokenType].brokersClaimRewards = brokersRewards[_broker][_tokenType]
        .brokersClaimRewards
        .add(rewards);
        emit CalcBrokerAmountA(
            _broker,
            currentRating,
            _amount,
            rewards,
            brokersRewards[_broker][_tokenType].brokersClaimRewards
        );
    } else if (currentRating <= BROKERSRATINGB) {
        // Ranking Level B
        uint256 rewards = _amount.mul(LevelBRewardNumerator).div(
            RewardPortionDenominator
        );
        brokersRewards[_broker][_tokenType].brokersClaimRewards = brokersRewards[_broker][_tokenType]
        .brokersClaimRewards
        .add(_amount);
        emit CalcBrokerAmountB(
            _broker,
            currentRating,
            _amount,
            rewards,
            brokersRewards[_broker][_tokenType].brokersClaimRewards
        );
    } else if (currentRating <= BROKERSLENGTH) {
```

## Recommendation
Revise the above calcBrokerAmount() function to properly compute the broker rewards.
