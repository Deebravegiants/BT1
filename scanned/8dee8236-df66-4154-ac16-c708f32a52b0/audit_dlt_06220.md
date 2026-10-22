# [M] `EtherFiNode` can’t move rewards to manager

## Summary
Severity: Medium
Chain: Smart contract
Component: ether-fi
Published: 2023-11-08
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/32
Type: hats-finding

## Details
**Github username:** @0xfuje
**Submission hash (on-chain):** 0x968c7b27073e2eef937359934daa5d0c71a63e63ca81789554b61d7664ec071a
**Severity:** medium

**Description:**
## Description
The `moveRewardsToManager()` function of `EtherFiNode` is restricted to only be callable from the manager contract and is expected to move rewards to `EtherFiNodeManager.sol`. However the problem is that the node manager can't possibly call this function because the call is currently unimplemented in the manager contract.

 `src/EtherFiNode.sol` - [`moveRewardsToManager()`](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/master/src/EtherFiNode.sol#L137-L144)
 
```solidity
    /// @notice Sends funds to the rewards manager
    /// @param _amount The value calculated in the etherfi node manager to send to the rewards manager
    function moveRewardsToManager(
        uint256 _amount
    ) external onlyEtherFiNodeManagerContract {
        (bool sent, ) = payable(etherFiNodesManager).call{value: _amount}("");
        require(sent, "Failed to send Ether");
    }
```
 
`src/EtherFiNode.sol` - [`onlyEtherFiNodeManagerContract()`](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/master/src/EtherFiNode.sol#L562-L568)
```solidity
    modifier onlyEtherFiNodeManagerContract() {
        require(
            msg.sender == etherFiNodesManager,
            "Only EtherFiNodeManager Contract"
        );
        _;
    }
```

## Recommendation
Consider either implementing the `moveRewardsToManager()` function in `EtherFiNodeManager.sol` or if the function serves no purpose currently: removing it from `EtherFiNode.sol`.
