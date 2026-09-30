# [M] AgentPolice._writeOffPools doesn't consider

## Summary
Severity: Medium
Contest weight: 0.4488
Dataset id: 20221
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
AgentPolice._writeOffPools doesn't consider interests. Because of that agent pays less then he should and pool doesn't earn. When agent is liquidated, then all funds that were received from it [will be returned ools/src/Agent/AgentPolice.sol#L222. This function will go through all pools and provide them amount of recovered funds dit/2023-06-glif/blob/main/pools/src/Agent/AgentPolice.sol#L413-L429
```solidity
for (i = 0; i < poolCount; ++i) {
    principal = AccountHelpers.getAccount(router, _agentID, _pools[i]).principal;
    principalAmts[i] = principal;
    totalPrincipal += principal;
}
for (i = 0; i < poolCount; ++i) {
    poolID = _pools[i];
    // compute this pool's share of the total amount
    poolShare = (principalAmts[i] * _totalAmount / totalPrincipal);
    // approve the pool to pull in WFIL
    IPool pool = GetRoute.pool(poolRegistry, poolID);
    wFIL.approve(address(pool), poolShare);
    // write off the pool's assets
    totalOwed = pool.writeOff(_agentID, poolShare);
    excessFunds += poolShare > totalOwed ? poolShare - totalOwed : 0;
}
```
It's just borrowed amount. When writeOff for pool is called, then pool uses provided values as payment of agent. Pool expects to receive interests as well, but AgentPolice doesn't know how much to send. Because of that next situation is possible: 1.there are 2 pool that agent used. Both of them has debt 1000:Butoneofthemhasallinterestsrepaidandanotheronehas5 debt. 2.for any reason agent is liquidated and there are exactly 2005$ to distribute. 3.share of each pool will be 1002.5 only. 4.first pool will use only 1000$ while another one will use 1002.5. 5.As result 2.5$ will be sent to agent's owner and second pool doesn't receive 2.5$. Liquidated funds are not used efficiently.

## Recommendation
You can make oracle calculate principal + interests that agent should pay for each pool and write off according to that info.
