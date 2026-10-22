# [M] Wrong Hardcoded Aave AToken Address

## Summary
Severity: Medium
Contest weight: 0.4301
Dataset id: 12770
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
DeFi protocols typically have a number of system-wide parameters that can be dynamically configured on demand. The Plexus protocol is no exception. Specifically, if we examine the constructor of the tier2Aave contract, it has defined a number of system-wide states: stakingContracts, stakingContractsStakingToken, tokenToAToken, and aTokenToToken. In the following, we show the related constructor.
```solidity
constructor() public payable {
    stakingContracts["DAI"] = 0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9;
    stakingContracts["ALL"] = 0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9;
    stakingContractsStakingToken["DAI"] = 0x25550Cccbd68533Fa04bFD3e3AC4D09f9e00Fc50;
    tokenToAToken[0x6B175474E89094C44Da98b954EedeAC495271d0F] = 0x25550Cccbd68533Fa04bFD3e3AC4D09f9e00Fc50;
    aTokenToToken[0x25550Cccbd68533Fa04bFD3e3AC4D09f9e00Fc50] = 0x6B175474E89094C44Da98b954EedeAC495271d0F;
    tokenToFarmMapping[stakingContractsStakingToken["DAI"]] = stakingContracts["DAI"];
    owner = msg.sender;
    admin = msg.sender;
}
```
It is important to ensure the correctness of these token contracts as they define various important aspects of the protocol operation and need to exercise extra care when configuring or updating it. It comes to our attention that the configured DAI and the associated aDAI mapping is incorrect. A misconﬁgured DAI/aDAI mapping could potentially result in loss of user funds!

## Recommendation
Validate these hard-coded token contracts and ensure they are consistent with the mainnet deployment.
