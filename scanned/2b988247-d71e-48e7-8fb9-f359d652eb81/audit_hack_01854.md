# [M] Impossible to remove malicious nodes after the initial period

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

The system has centralized power structure for the first year after deployment. An `unregisterKey` (creator of the contract) is allowed to remove Nodes that are in state `Stages.Active` from the registry, only in 1st year.

However, there is no possibility to remove malicious nodes from the registry after that.


**code/in3-contracts/contracts/NodeRegistry.sol:L249-L264**
```solidity
/// @dev only callable in the 1st year after deployment
function removeNodeFromRegistry(address _signer)
    external
    onlyActiveState(_signer)
{

    // solium-disable-next-line security/no-block-members
    require(block.timestamp < (blockTimeStampDeployment + YEAR_DEFINITION), "only in 1st year");// solhint-disable-line not-rely-on-time
    require(msg.sender == unregisterKey, "only unregisterKey is allowed to remove nodes");

    SignerInformation storage si = signerIndex[_signer];
    In3Node memory n = nodes[si.index];

    unregisterNodeInternal(si, n);

}
```

#### Recommendation

Provide a solution for the network to remove fraudulent node entries. This could be done by voting mechanism (with staking, etc).
