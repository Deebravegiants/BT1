# [M] Timely massUpdatePools During basePartition Update

## Summary
Severity: Medium
Contest weight: 0.4335
Dataset id: 13418
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Wombat protocol, the MasterWombatV3 contract is responsible to claim the WOM emissions from the Voter contract and distribute them to users. The claimed emissions are divided to two partitions, that are the base partition emissions and the boosted partition emissions. The base partition emissions are distributed to users per the amounts of their deposited LPs, and the boosted partition emissions are distributed per users boosted factors. The amount of base partition emissions is calculated from all the claimed emissions per the percentage basePartition, which can be dynamically updated by the owner via the updateEmissionPartition() routine. While analyzing the logic to update the basePartition in the updateEmissionPartition() routine, we notice the need of timely invoking the massUpdatePools() routine to accumulate the accWomPerShare/accWomPerFactorShare before the new basePartition gets eﬀective.
```solidity
function updateEmissionPartition(uint16 _basePartition) external onlyOwner {
    require(_basePartition <= 1000);
    basePartition = _basePartition;
    emit UpdateEmissionPartition(msg.sender, _basePartition, 1000 - _basePartition);
}
```
If the call to the massUpdatePools() is not immediately invoked before the new basePartition gets eﬀective, certain situations may be crafted to create an unfair reward distribution. Fortunately, this interface is restricted to the owner (via the onlyOwner modiﬁer), which greatly alleviates the concern.

## Recommendation
Timely invoke the massUpdatePools() at the beginning of the updateEmissionPartition() routine.
