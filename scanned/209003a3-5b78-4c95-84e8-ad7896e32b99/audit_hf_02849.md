# [C] Anyone can update the cluster address Impact: High, because a malicious user would gain access to a very important function. Likelihood: High, the lack of access control makes this function very easy to exploit.

## Summary
Severity: Critical
Contest weight: 0.3655
Dataset id: 15866
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In MagnetarV2.sol we have setCluster() function:
```solidity
function setCluster(ICluster _cluster) external {
    if (address(_cluster) == address(0)) revert NotValid();
    emit ClusterSet(cluster, _cluster);
    cluster = _cluster;
}
```
This function updates the cluster address, which is extremely important. But this function has no access control. Only the owner should be able to call this function. But currently absolutely anyone can call setCluster() and change the cluster address, which can cause major harm to the protocol.

## Recommendation
Add the onlyOwner modifier to the setCluster() function:
```solidity
function setCluster(ICluster _cluster) external onlyOwner {
    if (address(_cluster) == address(0)) revert NotValid();
    emit ClusterSet(cluster, _cluster);
    cluster = _cluster;
}
```
