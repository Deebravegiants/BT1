# [M] Lack of Protection Against Oversized Gauge/Type Weights

## Summary
Severity: Medium
Contest weight: 0.5936
Dataset id: 13367
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The VRH DAO is based on the CurveDAO where the GuildController contract is the center of the entire governance subsystem. In particular, this GuildController contract is responsible for adding new guilds and their types, changing their weights, as well as casting votes on different guilds. Our analysis leads to the discovery of a potential pitfall when a new oversized guild (or type) weight is updated on current pools. In particular, as the guild_relative_weight() routine involves the multiplication of three uint256 integer, it is possible for their multiplication to have an undesirable overflow (MULTIPLIER * _type_weight * _guild_weight in GuildController at line 456), especially when _type_weight or _guild_weight is largely controlled by an external entity. Fortunately, an authentication check is in place that effectively restricts the caller to be admin and thus greatly alleviates such concern.
```solidity
def _change_type_weight(type_id: int128, weight: uint256):
    @notice Change type weight
    @param type_id Type id
    @param weight New type weight
    old_weight: uint256 = self._get_type_weight(type_id)
    old_sum: uint256 = self._get_sum(type_id)
    _total_weight: uint256 = self._get_total()
    next_time: uint256 = (block.timestamp + WEEK) / WEEK * WEEK
    _total_weight = _total_weight + old_sum * weight - old_sum * old_weight
    self.points_total[next_time] = _total_weight
    self.points_type_weight[type_id][next_time] = weight
    self.time_total = next_time
    self.time_type_weight[type_id] = next_time
    log NewTypeWeight(type_id, next_time, weight, _total_weight)
```
However, any mis-configuration on the given weight may block the reward-claiming attempts of users who have staked on the affected guilds or types. If we use the change_type_weight() as an example, this issue is made possible if the weight amount is given as the argument to _change_type_weight() such that the calculation of MULTIPLIER * _type_weight * _guild_weight always overflows, hence reverting every guild_relative_weight() calculation of affected guilds in reward-claiming attempts. Note either only the specific guild with the misconfigured oversized weight or all guilds sharing the same oversized guild type will be affected.
```solidity
def _guild_relative_weight(addr: address, time: uint256) -> uint256:
    @notice Get Guild relative weight (not more than 1.0) normalized to 1e18 (e.g. 1.0 == 1e18). Inflation which will be received by it is inflation_rate * relative_weight / 1e18
    @param addr Guild address
    @param time Relative weight at the specified timestamp in the past or present
    @return Value of relative weight normalized to 1e18
    t: uint256 = time / WEEK * WEEK
    _total_weight: uint256 = self.points_total[t]
    if _total_weight > 0:
        guild_type: int128 = self.guild_types_[addr] - 1
        _type_weight: uint256 = self.points_type_weight[guild_type][t]
        _guild_weight: uint256 = self.points_weight[addr][t].bias
        return MULTIPLIER * _type_weight * _guild_weight / _total_weight
    else:
        return 0
```
To mitigate, it is best to apply a threshold check on the allowed weight update on a current guild or a supported guild type. Specifically, we can define TOTAL_WEIGHT_THRESHOLD that aims to restrict the total weight calculated from all current guilds. Therefore, for any change on a guild weight or a type weight, we can guarantee that the total weight is within an appropriate range. A candidate choice should be no larger than TOTAL_WEIGHT_THRESHOLD: constant(uint256)= convert(-1, uint256)/ MULTIPLIER.

## Recommendation
Add sanity checks to prevent the changed weight of a guild or an existing guild type from leading to an overflow calculation.
