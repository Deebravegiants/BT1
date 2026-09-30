# [M] `BondNFT.sol#claim

## Summary
Severity: Medium
Contest weight: 0.6393
Dataset id: 17361
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In `BondNFT.sol#claim()`, `accRewardsPerShare[][]` is amended to reflect the expired shares. But only `accRewardsPerShare[bond.asset][epoch[bond.asset]]` is updated. All the epochs between `bond.expireEpoch-1` and `epoch[bond.asset]` are missed.

However, some users claimable rewards calculation could be based on the missed epochs. As a result, the impact might be:

  * `accRewardsPerShare` is inaccurate for the epochs in between.
  * Some users could lose reward due to wrong `accRewardsPerShare`, some users might receive undeserved rewards.
  * Some rewards will be locked in the contract.

## Proof of Concept
The rationale behind the unchecked block below seems to take into account the shares of reward of the expired bond. However, if you only update the latest epoch data, the epochs in between could have errors and lead to loss of other users.
    
```solidity
function claim(
    uint _id,
    address _claimer
) public onlyManager() returns(uint amount, address tigAsset) {
    if (bond.expired) {
        uint _pendingDelta = (bond.shares * accRewardsPerShare[bond.asset][epoch[bond.asset]] / 1e18 - bondPaid[_id][bond.asset]) - (bond.shares * accRewardsPerShare[bond.asset][bond.expireEpoch-1] / 1e18 - bondPaid[_id][bond.asset]);
        if (totalShares[bond.asset] > 0) {
            accRewardsPerShare[bond.asset][epoch[bond.asset]] += _pendingDelta*1e18/totalShares[bond.asset];
        }
    }
    bondPaid[_id][bond.asset] += amount;
```

Users can claim rewards up to the expiry time, based on `accRewardsPerShare[tigAsset][bond.expireEpoch-1]`:
    
```solidity
function idToBond(uint256 _id) public view returns (Bond memory bond) {
    bond.expired = bond.expireEpoch <= epoch[bond.asset] ? true : false;
    unchecked {
        uint _accRewardsPerShare = accRewardsPerShare[bond.asset][bond.expired ? bond.expireEpoch-1 : epoch[bond.asset]];
        bond.pending = bond.shares * _accRewardsPerShare / 1e18 - bondPaid[_id][bond.asset];
```

Acknowledged, we cant redistribute past rewards accurately because it would cost too much gas.

I would downgrade it to Medium risk, needs an opinion from judge.

The Warden has shown how, due to how epochs are handled, some rewards could be lost unless claimed each epoch.

Because the finding pertains to a loss of Yield, I agree with Medium Severity.

It is not feasible to update accRewardsPerShare for every epoch during which bond was expired. This issue is mitigated by the fact that anyone can release an expired bond, so the small difference in yield shouldn’t affect users that much.

## Recommendation
No recommendation
