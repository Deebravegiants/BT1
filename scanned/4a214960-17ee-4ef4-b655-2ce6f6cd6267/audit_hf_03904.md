# [H] Funds not withdrawable because configuredForTakeover

## Summary
Severity: High
Contest weight: 0.7869
Dataset id: 20203
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
configuredForTakeover which is called when a user adds a miner to the agent allows to add miners with expired beneficiary addresses. However - there is no functionality in the agent to change the beneficiary to the agent address. Therefore - an agent will not be able to call pullFunds from the miner which could lead to inability to pay pool debt as expected and repay protocol debt therefore lose of funds.
dit/2023-06-glif/blob/main/pools/src/Agent/Agent.sol#L155
```solidity
function addMiner(
    SignedCredential calldata sc
) external onlyOwnerOperator validateAndBurnCred(sc) checkVersion {
    // confirm the miner is valid and can be added
    if (!sc.vc.target.configuredForTakeover()) revert Unauthorized();
    // change the owner address
    sc.vc.target.changeOwnerAddress(address(this));
    // add the miner to the central registry, this call will revert if the miner is already registered
    minerRegistry.addMiner(id, sc.vc.target);
}
```
Helper.sol#L80 configuredForTakeover actively permits miners that have an expired beneficiary
```solidity
function configuredForTakeover(uint64 target) internal returns (bool) {
    CommonTypes.FilActorId minerId = _getMinerId(target);
    MinerTypes.GetBeneficiaryReturn memory ret = MinerAPI.getBeneficiary(minerId);
    // if the beneficiary address is the miner's owner, then the agent will assume beneficiary
    if (_getOwner(minerId) == PrecompilesAPI.resolveAddress(ret.active.beneficiary)) {
        return true;
    }
    // if the beneficiary address is expired, then Agent will be ok to take ownership
    MinerTypes.BeneficiaryTerm memory term = ret.active.term;
    uint256 expiration = uint256(uint64(CommonTypes.ChainEpoch.unwrap(term.expiration)));
    if (expiration < block.number) return true;
    return false;
}
```
The issue is that in such case the agent owner cannot call pullFunds since the miner withdrawBalance will fail as the owner is not the beneficiary and the beneficiary has expired: https://github.com/filecoin-project/builtin-actors/blob/master/actors/miner/src/lib.rs#L3293
Agent will not be able to:
1. withdraw funds from miner to agent. This can lead to inability to pay debt to pool
2. repay debt to the protocol (lead to more slashing)

## Recommendation
Either:
1. Not allow expired beneficiary
2. Add a changeBeneficiary function in the agent that calls the miner changeBeneficiary() function with the agent address
