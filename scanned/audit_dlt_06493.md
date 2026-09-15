# [M] `LM_PC_KPIRewarder_v1` if bond token has a blocklist and disputer set disputer address to a blocked address, result in DoS

## Summary
Severity: Medium
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-08
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/75
Type: hats-finding

## Details
**Github username:** @NicolaMirchev
**Twitter username:** EgisSec
**Submission hash (on-chain):** 0x4c23a8b0e13a17a6383ffa4cac3ade98fe84fd37d206399f31df8c4ddcc5bb61
**Severity:** medium

**Description:**
**Description**\
In [LM_PC_KPIRewarder_v1](https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/blob/62892384fd7d0ce4d0e389c530200c69921473f7/src/modules/logicModule/LM_PC_KPIRewarder_v1.sol#L156-L161) an asserter creates assertation to UMA oracle posting KPI data. UMA oracle accepts bond in different currencies, which is used to incertivies disputers and asserters to tell the truth. This `defaultCurrency` can be USDC/USDT, both of which has a blocklist functionality. The problem here is that if by any chance/mistake asserter has posted wrong info, untrusted diputer is able to [dispute](https://github.com/UMAprotocol/protocol/blob/6ef5fe9d2fa5545c079603f8cd20f976aeb23295/packages/core/contracts/optimistic-oracle-v3/implementation/OptimisticOracleV3.sol#L220) the assertation and provide arbitrary address as `disputer`. This address later [recieves the bond reward](https://github.com/UMAprotocol/protocol/blob/6ef5fe9d2fa5545c079603f8cd20f976aeb23295/packages/core/contracts/optimistic-oracle-v3/implementation/OptimisticOracleV3.sol#L271-L280), if dispute has been successful. The following would result in DoS of UMA [settleAssertion](https://github.com/UMAprotocol/protocol/blob/6ef5fe9d2fa5545c079603f8cd20f976aeb23295/packages/core/contracts/optimistic-oracle-v3/implementation/OptimisticOracleV3.sol#L250C14-L250C29) function, which result in unreachability of [LM_PC_KPIRewarder_v1::assertionResolvedCallback](https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/blob/62892384fd7d0ce4d0e389c530200c69921473f7/src/modules/logicModule/LM_PC_KPIRewarder_v1.sol#L349) and so the whole `LM_PC_KPIRewarder_v1` logic, because it would be impossible to create new assertions, before we have set `assertionPending` to false. 

**Attack Scenario**\
1. There is a KPI staking module with trusted asserters, who frequently post asserts to UMA
2. Asserter then posts KPI with some data, but after 2 hours, we see that the info is not correct and an expoiter who monitors for unvalid assertations strikes.
3. He opens a dispute, knowing that he will win, because of the wrongness of the data.
4. He set up a blocklisted address as `disputer`.
5. `LM_PC_KPIRewarder_v1` is DoSed and no rewards could be accured, because there is pending assertation stucked

**Attachments**

1. **Proof of Concept (PoC) File**
Will provide if needed

2. **Revised Code File (Optional)**
Implement some kind of `backup` logic, which could be opening a new assertation asserting `Contract is stucked, because assertion {id} could not be proceed`. The following could be opened by `Asserter`, only if `assertionPending = true` and when it is resolved, it should make back `assertionPending = false`
