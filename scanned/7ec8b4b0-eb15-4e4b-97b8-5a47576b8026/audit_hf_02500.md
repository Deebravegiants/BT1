# [M] Implicit Threshold On Supported Distinct Guild Types

## Summary
Severity: Medium
Contest weight: 0.7022
Dataset id: 13368
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In VRH DAO, there is an implicit restriction on the number of guild types that can be supported. However, this restriction is not enforced when a new guild type is being added. As a result, if a new guild type is assigned with an type id that exceeds the limit, the new guild type as well as all guilds of this guild type will not be able to participate in the governance token distribution.
```solidity
def _get_total() -> uint256:
    @notice Fill historic total weights week-over-week for missed checkins and return the total for the future week
    @return Total weight
    t: uint256 = self.time_total
    _n_guild_types: int128 = self.n_guild_types
    if t > block.timestamp:
        # If we have already checkpointed - still need to change the value
        t -= WEEK
    pt: uint256 = self.points_total[t]
    for guild_type in range(100):
        if guild_type >= _n_guild_types:
            break
        self._get_sum(guild_type)
        self._get_type_weight(guild_type)
    for i in range(500):
        if t > block.timestamp:
            break
        t += WEEK
        pt = 0
        # Scales as n_types * n_unchecked_weeks (hopefully 1 at most)
        for guild_type in range(100):
            if guild_type >= _n_guild_types:
                break
            type_sum: uint256 = self.points_sum[guild_type][t].bias
            type_weight: uint256 = self.points_type_weight[guild_type][t]
            pt += type_sum * type_weight
        self.points_total[t] = pt
    if t > block.timestamp:
        self.time_total = t
    return pt
```
Apparently, as shown in the line 318, only the first 100 guild types are taken into consideration, excluding all other guild types and their guilds from participating in the distribution of governance tokens.
```solidity
def add_type(_name: String[64], _symbol: String[32], gas_addr: address, weight: uint256 = 0):
    @notice Add guild type with name _name and weight weight
    @param _name Name of guild type
    @param gas_addr Address of the gas token
    @param weight Weight of guild type
    assert msg.sender == self.admin
    assert self.gas_addr_escrow[gas_addr] == ZERO_ADDRESS, "Already has gas escrow" # one gas token can only have one gas escrow
    escrow_addr: address = create_forwarder_to(self.gas_escrow)
    _isSuccess: bool = GasEscrow(escrow_addr).initialize(self.admin, gas_addr, _name, _symbol)
    if _isSuccess:
        type_id: int128 = self.n_guild_types
        self.guild_type_names[type_id] = _name
        self.n_guild_types = type_id + 1
        if weight != 0:
            self._change_type_weight(type_id, weight)
        self.gas_type_escrow[type_id] = escrow_addr
        self.gas_addr_escrow[gas_addr] = escrow_addr
        log AddType(_name, type_id, gas_addr, weight, escrow_addr)
```
Meanwhile, the add_type() routine that handles the addition of new types is not enforcing the above (implicit) limit. With that, it is strongly suggested to define the MAX_GUILD_TYPES and make the limit explicit. This explicit limit is necessary as we observe blurred or confused declaration of the number of guild types reflected in other data structures. For example, both time_sum and time_type_weight denote the mapping from a specific guild type to the last scheduled time of all guild of the same type and the type weight respectively. The current declaration (line 150 and 156) misleadingly indicate the protocol support 1,000,000,000 types! By having the explicit limit, we can re-define both time_sum and time_type_weight in an unambiguous manner that greatly reduces the storage reservation from 1,000,000,000 to 100, i.e., time_sum: public(uint256[100]) and time_type_weight: public(uint256[100]).
```solidity
time_sum: public(uint256[1000000000]) # type_id -> last scheduled time (next week)
points_total: public(HashMap[uint256, uint256]) # time -> total weight
time_total: public(uint256) # last scheduled time
points_type_weight: public(HashMap[int128, HashMap[uint256, uint256]]) # type_id time -> type weight
time_type_weight: public(uint256[1000000000]) # type_id -> last scheduled time (next week)
```

## Recommendation
Explicitly limit the number of guild types that can be supported in the protocol and enforce the limit when a new type is being added.
```solidity
MAX_GAUGE_TYPES: constant(uint256) = 100
def add_type(_name: String[64], _symbol: String[32], gas_addr: address, weight: uint256 = 0):
    @notice Add guild type with name _name and weight weight
    @param _name Name of guild type
    @param gas_addr Address of the gas token
    @param weight Weight of guild type
    assert msg.sender == self.admin
    assert self.gas_addr_escrow[gas_addr] == ZERO_ADDRESS, "Already has gas escrow" # one gas token can only have one gas escrow
    escrow_addr: address = create_forwarder_to(self.gas_escrow)
    _isSuccess: bool = GasEscrow(escrow_addr).initialize(self.admin, gas_addr, _name, _symbol)
    if _isSuccess:
        type_id: int128 = self.n_guild_types
        assert type_id < MAX_GAUGE_TYPES
        self.guild_type_names[type_id] = _name
        self.n_guild_types = type_id + 1
        if weight != 0:
            self._change_type_weight(type_id, weight)
        self.gas_type_escrow[type_id] = escrow_addr
        self.gas_addr_escrow[gas_addr] = escrow_addr
        log AddType(_name, type_id, gas_addr, weight, escrow_addr)
```
