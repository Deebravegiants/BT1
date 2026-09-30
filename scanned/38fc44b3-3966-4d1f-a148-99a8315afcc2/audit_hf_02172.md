# [M] Possible DoS Attack in Contribute()

## Summary
Severity: Medium
Contest weight: 0.6067
Dataset id: 12115
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the GatherCore contract, the internal function contribute() updates the states regarding each user's contribution as well as the global states (e.g., totalPoolContribution). During each contribute() call, the _value is checked against minContribution (line 60) and maxContribution (line 61). Also, the totalPoolContribution + _value is not allowed to be greater than maxPoolAllocation (line 62). However, those constraints create an attack surface for denial-of-services. For example, let's say maxPoolAllocation=100 and minContribution=10. When totalPoolContribution reaches 80, a bad actor could intentionally contribute() 11, which passes all the sanity checks but denies all the following contributions. Speciﬁcally, the totalPoolContribution after the bad actor's contribution would be 80 + 11 = 91. No contribution which passes both checks in line 60 and line 62 could be made since 91 + 10 = 101 > 100.

```solidity
function contribute(address _sender, uint256 _value)
    internal
    isPoolOpen()
    Contributor storage contributor = contributorsInfo[_sender];
    require(_value > 0, "ZERO_AMOUNT_SENT");
    uint256 poolContributionSum = totalPoolContribution.add(_value);
    require(_value >= minContribution, "AMNT < MIN_CNTRBUTN_ALWD");
    require(_value <= maxContribution, "AMNT > MAX_CNTRBUTN_ALWD");
    require(
        poolContributionSum <= maxPoolAllocation,
        "TOTAL_POOL_CONTRIBUTION_EXCEED"
    );
    if (contributor.exists) {
        uint256 balanceSum = contributor.balance.add(_value);
        require(
            balanceSum <= maxContribution,
            "TTL_CNTRBUTN > MX_CNTRBUTN_ALWD"
        );
    } else {
        contributor.exists = true;
        contributors.push(_sender);
    }
    contributor.balance = contributor.balance.add(_value);
    // Update the total pool value
    totalPoolContribution = totalPoolContribution.add(_value);
    // Update fund raised
```

## Recommendation
Update minContribution for the last contribution if necessary.

```solidity
function contribute(address _sender, uint256 _value)
    internal
    isPoolOpen()
    Contributor storage contributor = contributorsInfo[_sender];
    require(_value > 0, "ZERO_AMOUNT_SENT");
    uint256 poolContributionSum = totalPoolContribution.add(_value);
    require(_value >= minContribution, "AMNT < MIN_CNTRBUTN_ALWD");
    require(_value <= maxContribution, "AMNT > MAX_CNTRBUTN_ALWD");
    require(
        poolContributionSum <= maxPoolAllocation,
        "TOTAL_POOL_CONTRIBUTION_EXCEED"
    );
    if (contributor.exists) {
        uint256 balanceSum = contributor.balance.add(_value);
        require(
            balanceSum <= maxContribution,
            "TTL_CNTRBUTN > MX_CNTRBUTN_ALWD"
        );
    } else {
        contributor.exists = true;
        contributors.push(_sender);
    }
    contributor.balance = contributor.balance.add(_value);
    // Update the total pool value
    totalPoolContribution = poolContributionSum;
    // Update minContribution for the last contributor
    minContribution = minContribution <= maxPoolAllocation.sub(totalPoolContribution)
        ? minContribution
        : maxPoolAllocation.sub(totalPoolContribution);
    // Update fund raised
```
