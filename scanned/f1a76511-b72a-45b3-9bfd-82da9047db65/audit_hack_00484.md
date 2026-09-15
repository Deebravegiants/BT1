# [M] SubQuery Network incident: Attackers exploited a vulnerability in SubQuery Network’s Settings contract on the Base network (the setContractAddress() function

## Summary
Severity: Medium
Target: SubQuery Network
Loss: $ 134,000
Attack method: Smart Contract Vulnerability
Published: 2026-04-12
Source: https://subquery.network/blog/subquery-network-security-incident-report
Type: slowmist-incident

## Details
Attackers exploited a vulnerability in SubQuery Network’s Settings contract on the Base network (the setContractAddress() function missing the onlyOwner access control modifier). By repeatedly calling this function, the attacker set their address as StakingManager and RewardsDistributor, enabling drainage of pooled SQT from the Staking contract, impacting 272 individual staker/delegator wallets, RewardsBooster, and a small protocol Treasury. Approximately 382,433,441 SQT were drained (worth about $134,000 USD at the time). The team quickly responded by deploying a fix, pausing withdrawals, and committing to full compensation for all affected users. No user private keys were compromised. The root cause was a missing access control from a prior code refactor.
